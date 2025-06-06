from pathlib import Path
from time import sleep
import os
from django.http import HttpRequest, HttpResponse

from hstream.hs import hs as hs_type
from hstream.template import error_html, format_html
from hstream.utils import pick_a_strategy, split_code_into_blocks

from .session_utils import get_session_var, set_session_var


def request_server_stop_running_user_script(request, wait=True):
    if wait:
        while get_session_var(request, "hs_script_running", False):
            set_session_var(request, "hs_script_should_stop", True)
            sleep(0.1)
    else:
        set_session_var(request, "hs_script_should_stop", True)
    set_session_var(request, "hs_html", "")


def index(request: HttpRequest):
    if len(request.session.keys()) > 0:
        request.session.clear()
        request.session.save()
    request_server_stop_running_user_script(request, wait=True)
    set_session_var(request, "hs_html_last_sent", "")
    set_session_var(request, "hs_html", "")
    return HttpResponse(format_html())


def run_hs(request):
    if get_session_var(request, "hs_script_running", False):
        HttpResponse("already running")
    set_session_var(request, "hs_script_running", True)
    try:

        # TODO: I'm sure theres a way to pass this filename from django through the cli :thinking
        hs: hs_type = run_user_code_and_return_hs_instance(
            os.environ["HS_FILE_TO_RUN"], request
        )
    except Exception as e:
        set_session_var(request, "hs_script_running", False)
        set_session_var(
            request,
            "hs_html",
            get_session_var(request, "hs_html", "") + error_html.format(error=e),
        )
        return HttpResponse(f"error: {e}")
    set_session_var(request, "hs_script_running", False)
    response = HttpResponse(hs.doc.getvalue())
    hs.clear()  # we should always clear the hs element otherwise we get ghost elements on next run
    response["HX-Trigger"] = "update_content_event"
    return response


def partial_or_full_html_content(request):
    """
    Decides wether to send
    1. full html content and replace existing content
    2. nothing
    3. partial html content and replace existing content partially
    4. partial html content and append to existing content

    We aim to balance simplicity, user interactivity, minimal updates to frontend
    (so user doesn't see weird behaviour)

    Decision is based on internal conditions of what was last sent, current html
    content and if the script is running - see: contribution_docs/update_strategies.md
    """
    from hstream.utils import check_duplicate_ids_is_present, get_hs_ids_with_content

    html = get_session_var(request, "hs_html", "")
    prev_html = get_session_var(request, "hs_html_last_sent", None)

    if check_duplicate_ids_is_present(html):
        html += error_html.format(
            error=f"Duplicate ids found in the html: {check_duplicate_ids_is_present(html)}"
        )

    update_strategy = pick_a_strategy(
        prev_html, html, get_session_var(request, "hs_script_running", False)
    )
    # print(f"update strategy: {update_strategy}")
    response = HttpResponse()
    if get_session_var(request, "hs_script_running", False):
        response.headers["HX-Trigger"] = "update_content_event"

    if update_strategy == "1_full_replace":
        set_session_var(request, "hs_html_partial_keys_updated", [])
        set_session_var(request, "hs_html_last_sent", html)
        response.content = html
        return response
    elif update_strategy == "2_nothing":
        response.headers["HX-Reswap"] = "none"
        response.headers["HX-Target"] = "none"
        return response
    elif update_strategy == "3_partial_replace":
        current_hs_ids_and_content = get_hs_ids_with_content(html)
        prev_hs_ids_and_content = get_hs_ids_with_content(prev_html)
        for old_key, old_value in prev_hs_ids_and_content.items():
            if old_key in get_session_var(request, "hs_html_partial_keys_updated", []):
                break
            new_value = current_hs_ids_and_content.get(old_key, False)
            if new_value:
                if old_value != new_value:
                    set_session_var(
                        request,
                        "hs_html_partial_keys_updated",
                        get_session_var(request, "hs_html_partial_keys_updated", [])
                        + [old_key],
                    )
                    response.headers["HX-Target"] = f"#{old_key}"
                    response.headers["HX-Reswap"] = "innerHTML"
                    print("partial html sent")
                    return new_value
        # if we reach here we swap to full replacement strategy
        response.headers["HX-Reswap"] = "none"
        response.headers["HX-Target"] = "none"
        return response
    elif update_strategy == "4_partial_append":
        # handle the case where script is running for the first time so current is more complete than old
        # and we want to append the new content to the old content
        set_session_var(request, "hs_html_partial_keys_updated", [])
        set_session_var(request, "hs_html_last_sent", html)
        response.headers["HX-Reswap"] = "beforeend"
        response.content = html.replace(prev_html, "")
        return response
    else:
        raise ValueError(f"Unknown update strategy: {update_strategy}")


def run_user_code_and_return_hs_instance(file: Path, request: HttpRequest) -> hs_type:
    users_hs_instance = None
    moneky_pathed__builtins__ = __builtins__
    moneky_pathed__builtins__["_hs_session"] = request.session
    namespace = {"__builtins__": moneky_pathed__builtins__}
    try:
        code = open(file).read()
        for line, block in enumerate(split_code_into_blocks(code)):
            if get_session_var(request, "hs_script_should_stop", False):
                break
            compiled_code = compile(block, f"HS_STREAM_USER_FILE_LINE_{line}", "exec")
            exec(
                compiled_code,
                namespace,
            )
        try:
            for var_name, var_value in namespace.items():
                if var_value.__class__.__name__ == "hs":
                    users_hs_instance = var_value
            if users_hs_instance is None:
                raise ValueError(
                    "Seems your file does not import hs `from hstream import hs`"
                )
            html = users_hs_instance.doc.getvalue()
            # TODO: if the script sets component values we should honour these as well
            # for example a button reverting itself back to false after being clicked
            request.session = namespace["__builtins__"]["_hs_session"]
            set_session_var(request, "hs_html", html)
        except ValueError as e:
            if (
                e.args[0]
                == "Seems your file does not import hs `from hstream import hs`"
            ):
                raise e
        except:  # noqa #E722
            pass
    except Exception as e:
        e.args = (f"Line: {line}, code: {block}", *e.args)
        raise e
    finally:
        set_session_var(request, "hs_script_should_stop", False)
    return users_hs_instance
import os
import tempfile
from pathlib import Path

def set_component_value(
    request: HttpRequest,
):
    component_id = request.GET.get("component_id")
    
    request_server_stop_running_user_script(request, wait=True)
    
    # Handle file uploads
    if request.FILES and "new_value" in request.FILES:
        uploaded_file = request.FILES["new_value"]
        
        # Create tmp directory if it doesn't exist
        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)
        
        # Save file to tmp directory
        file_path = tmp_dir / uploaded_file.name
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        # Set the filename as the value
        new_value = uploaded_file.name
        print(f'File saved to: {file_path}')
        
    else:
        # Handle regular form data
        new_value = request.POST.get("new_value")
        if new_value is None:
            new_value = request.GET.get("new_value")
    
    set_session_var(request, component_id, new_value)
    print('Component value set to:', new_value)
    
    response = HttpResponse(f"suc: {request.session[component_id]}", status=200)
    response.headers["HX-Reswap"] = "none"
    response.headers["HX-Trigger"] = "trigger_run_hs_event"
    return response
