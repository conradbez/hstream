import traceback
from hstream.template import format_html, error_html
import cherrypy
from hstream.utils import set_session_var
from pathlib import Path
from hstream.utils import split_code_into_blocks


def run_user_code_and_return_hs_instance(file: Path):
    users_hs_instance = None
    namespace = {}
    set_session_var("hs_html", "")
    try:
        code = open(file).read()
        for line, block in enumerate(split_code_into_blocks(code)):
            if cherrypy.session.get("hs_script_should_stop", False):
                set_session_var("hs_script_should_stop", False)
                break
            compiled_code = compile(block, f"HS_STREAM_USER_FILE_LINE_{line}", "exec")
            exec(compiled_code, namespace)
    except Exception as e:
        e.args = (f"Line: {line}, code: {block}", *e.args)
        raise e
    finally:
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
        while cherrypy.session.get("hs_script_running", False):
            from time import sleep

            set_session_var("hs_script_should_stop", True)
            sleep(0.1)

        cherrypy.session.acquire_lock()
        cherrypy.session.clear()
        cherrypy.session.release_lock()
        set_session_var("hs_html", "")
        set_session_var("hs_html_last_sent", "")
        return format_html()

    @cherrypy.expose
    def run_hs(self):
        if cherrypy.session.get("hs_script_running", False):
            # cherrypy.response.status = 204
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
            cherrypy.response.status = 204
            print(e)
            return "error"
        set_session_var("hs_script_running", False)
        cherrypy.response.headers["HX-Trigger"] = "update_content_event"
        cherrypy.response.status = 204
        return "suc"

    @cherrypy.expose
    def partial_or_full_html_content(self):
        html = cherrypy.session.get("hs_html", "")
        from hstream.utils import check_duplicate_ids_is_present

        if check_duplicate_ids_is_present(html):
            html += error_html.format(
                error=f"Duplicate ids found in the html: {check_duplicate_ids_is_present(html)}"
            )

        if cherrypy.session.get("hs_script_running", True):
            cherrypy.response.headers["HX-Trigger"] = "update_content_event"

        last_sent_html = cherrypy.session.get("hs_html_last_sent", None)
        set_session_var("hs_html_last_sent", html)
        if last_sent_html == None:
            return html

        elif not last_sent_html == html[: len(last_sent_html)]:
            # wont reuse users html
            return html

        else:
            # will re-use existing html
            # cherrypy.response.headers["HX-Retarget"] = "#hs-content"
            cherrypy.response.headers["HX-Reswap"] = "beforeend"
            if last_sent_html == html:
                return ""
            elif last_sent_html == html[: len(last_sent_html)]:
                return html.replace(last_sent_html, "")
            else:
                set_session_var("hs_html_last_sent", "")
                cherrypy.response.status = 500
                return "an error occured"

    @cherrypy.expose
    def set_component_value(self, component_id, new_value=None, *args, **kwargs):
        if new_value == None:
            new_value = kwargs
        set_session_var(component_id, new_value)
        cherrypy.response.headers["HX-Trigger"] = "trigger_run_hs_event"
        return f"suc: {cherrypy.session[component_id]}"
