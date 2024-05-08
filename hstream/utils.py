import cherrypy


def set_session_var(component_id, new_value):
    cherrypy.session.acquire_lock()
    cherrypy.session[component_id] = new_value
    cherrypy.session.release_lock()
    return


def check_duplicate_ids_is_present(html):
    import bs4
    import collections

    soup = bs4.BeautifulSoup(html, features="html.parser")
    ids = [a.attrs["id"] for a in soup.find_all(attrs={"id": True})]
    ids = collections.Counter(ids)
    dups = [key for key, value in ids.items() if value > 1]

    return dups if len(dups) > 0 else False

import ast

def split_code_into_blocks(code:str):
    tree = ast.parse(code)
    blocks = []

    for node in ast.iter_child_nodes(tree):
        block = ast.unparse(node)
        blocks.append(block)
            
    # import ipdb; ipdb.set_trace()
    return blocks
