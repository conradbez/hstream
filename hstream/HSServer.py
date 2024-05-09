import traceback
from hstream.template import format_html, error_html
import cherrypy
from hstream.utils import set_session_var, split_code_into_blocks, pick_a_strategy
from pathlib import Path
from time import sleep


def request_server_stop_running_user_script(wait=True):
    if wait:
        while cherrypy.session.get("hs_script_running", False):
            set_session_var("hs_script_should_stop", True)
            sleep(0.1)
    else:
        set_session_var("hs_script_should_stop", True)
    set_session_var("hs_html", "")


def run_user_code_and_return_hs_instance(file: Path):
    users_hs_instance = None
    namespace = {}
    try:
        code = open(file).read()
        for line, block in enumerate(split_code_into_blocks(code)):
            if cherrypy.session.get("hs_script_should_stop", False):
                break
            compiled_code = compile(block, f"HS_STREAM_USER_FILE_LINE_{line}", "exec")
            exec(compiled_code, namespace)
    except Exception as e:
        e.args = (f"Line: {line}, code: {block}", *e.args)
        raise e
    finally:
        set_session_var("hs_script_should_stop", False)
        for var_name, var_value in namespace.items():
            if var_value.__class__.__name__ == "hs":
                users_hs_instance = var_value
                # we should always clear the hs element otherwise we get ghost elements on next run
                users_hs_instance.clear()
                # users_hs_instance.doc, users_hs_instance.tag, users_hs_instance.text = Doc().tagtext()
    return users_hs_instance


class RootServerPathWorld(object):
    def __init__(self, file: Path):
        self.file = file

    @cherrypy.expose
    def index(self):
        request_server_stop_running_user_script(wait=True)
        cherrypy.session.acquire_lock()
        cherrypy.session.clear()
        cherrypy.session.release_lock()
        set_session_var("hs_html_last_sent", "")
        return format_html()

    @cherrypy.expose
    def run_hs(self):
        # cherrypy.response.status = 204
        if cherrypy.session.get("hs_script_running", False):
            return "already running"
        set_session_var("hs_script_running", True)
        try:
            hs = run_user_code_and_return_hs_instance(self.file)
        except Exception as e:
            set_session_var("hs_script_running", False)
            set_session_var(
                "hs_html",
                cherrypy.session.get("hs_html", "") + error_html.format(error=e),
            )
            print(e)
            return "error"
        set_session_var("hs_script_running", False)
        cherrypy.response.headers["HX-Trigger"] = "update_content_event"
        return "suc"

    @cherrypy.expose
    def partial_or_full_html_content(self):
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
        from hstream.utils import (
            check_duplicate_ids_is_present,
            get_hs_ids_with_content,
        )

        html = cherrypy.session.get("hs_html", "")
        prev_html = cherrypy.session.get("hs_html_last_sent", None)

        if check_duplicate_ids_is_present(html):
            html += error_html.format(
                error=f"Duplicate ids found in the html: {check_duplicate_ids_is_present(html)}"
            )

        update_strategy = pick_a_strategy(
            prev_html, html, cherrypy.session.get("hs_script_running", False)
        )
        # print(f"update strategy: {update_strategy}")

        if cherrypy.session.get("hs_script_running", False):
            cherrypy.response.headers["HX-Trigger"] = "update_content_event"

        if update_strategy == "1_full_replace":
            set_session_var("hs_html_partial_keys_updated", [])
            set_session_var("hs_html_last_sent", html)
            return html
        elif update_strategy == "2_nothing":
            cherrypy.response.headers["HX-Reswap"] = "none"
            cherrypy.response.headers["HX-Target"] = "none"
            return ""
        elif update_strategy == "3_partial_replace":
            current_hs_ids_and_content = get_hs_ids_with_content(html)
            prev_hs_ids_and_content = get_hs_ids_with_content(prev_html)
            for old_key, old_value in prev_hs_ids_and_content.items():
                if old_key in cherrypy.session.get("hs_html_partial_keys_updated", []):
                    break
                new_value = current_hs_ids_and_content.get(old_key, False)
                if new_value:
                    if old_value != new_value:
                        set_session_var(
                            "hs_html_partial_keys_updated",
                            cherrypy.session.get("hs_html_partial_keys_updated", [])
                            + [old_key],
                        )
                        cherrypy.response.headers["HX-Target"] = f"#{old_key}"
                        cherrypy.response.headers["HX-Reswap"] = "innerHTML"
                        print("partial html sent")
                        return new_value
            # if we reach here we swap to full replacement strategy
            cherrypy.response.headers["HX-Reswap"] = "none"
            cherrypy.response.headers["HX-Target"] = "none"
            return ""
        elif update_strategy == "4_partial_append":
            # handle the case where script is running for the first time so current is more complete than old
            # and we want to append the new content to the old content
            set_session_var("hs_html_partial_keys_updated", [])
            set_session_var("hs_html_last_sent", html)
            cherrypy.response.headers["HX-Reswap"] = "beforeend"
            return html.replace(prev_html, "")
        else:
            raise ValueError(f"Unknown update strategy: {update_strategy}")
        # panic and just send the new html
        set_session_var("hs_html_last_sent", html)
        set_session_var("hs_html_partial_keys_updated", [])
        return html

    @cherrypy.expose
    def set_component_value(self, component_id, new_value=None, *args, **kwargs):
        request_server_stop_running_user_script(wait=True)
        if new_value == None:
            new_value = kwargs
        set_session_var(component_id, new_value)
        cherrypy.response.headers["HX-Trigger"] = "trigger_run_hs_event"
        return f"suc: {cherrypy.session[component_id]}"
