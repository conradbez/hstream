import cherrypy
import ast
import bs4
import collections
from typing import Literal


def set_session_var(component_id, new_value):
    cherrypy.session.acquire_lock()
    cherrypy.session[component_id] = new_value
    cherrypy.session.release_lock()
    return


def check_duplicate_ids_is_present(html):
    soup = bs4.BeautifulSoup(html, features="html.parser")
    ids = [a.attrs["id"] for a in soup.find_all(attrs={"id": True})]
    ids = collections.Counter(ids)
    dups = [key for key, value in ids.items() if value > 1]

    return dups if len(dups) > 0 else False


def get_hs_ids_with_content(html: str):
    soup = bs4.BeautifulSoup(html, "html.parser")
    ids = [a.attrs["id"] for a in soup.find_all(attrs={"id": True})]
    hs_ids = list(
        filter(lambda x: x.startswith("container_for_HSSTREAMUSERFILELINE"), ids)
    )
    hs_content = {_id: soup.find(id=_id).encode_contents() for _id in hs_ids}
    return hs_content


def split_code_into_blocks(code: str):
    tree = ast.parse(code)
    blocks = []

    for node in ast.iter_child_nodes(tree):
        block = ast.unparse(node)
        blocks.append(block)

    # import ipdb; ipdb.set_trace()
    return blocks


def pick_a_strategy(
    prev_html, new_html, hs_script_running=False
) -> Literal["1_full_replace", "2_nothing", "3_partial_replace", "4_partial_append"]:
    """
    Pick how we want to update the html

    See: contribution_docs/update_strategies.md
    """
    current_hs_ids_and_content = get_hs_ids_with_content(new_html)
    prev_hs_ids_and_content = get_hs_ids_with_content(prev_html)
    current_hs_ids = list(current_hs_ids_and_content.keys())
    prev_hs_ids = list(prev_hs_ids_and_content.keys())

    if prev_html == None or not hs_script_running:
        return "1_full_replace"

    elif prev_html == new_html:
        return "2_nothing"

    # current id length is shorter than prev id length AND;
    # current id's are all contained in prev ids
    elif len(current_hs_ids) <= len(prev_hs_ids) and set(current_hs_ids).issubset(
        set(prev_hs_ids)
    ):
        return "3_partial_replace"
    # current id lengths are greater than previous AND;
    # prev ids are all contained in current id AND;
    # where there are prev html values they are the same as current html values
    elif (
        len(current_hs_ids) > len(prev_hs_ids)
        and set(prev_hs_ids).issubset(set(current_hs_ids))
        and (
            list(current_hs_ids_and_content.values())[: len(prev_hs_ids)]
            == list(prev_hs_ids_and_content.values())
        )
    ):
        return "4_partial_append"
    else:
        raise ValueError("Strategy not found")
