# %%
import ast
import ast_scope

code = """
text_entered = hs.text_input(text = 'text_input_label', default_value='default_value', key = 'my_input')
hs.write(text_entered, key = 'my_write')

print(text_entered, 'in main.py')
"""


# %%
tree = ast.parse(code)
scope_info = ast_scope.annotate(tree)
global_variables = sorted(scope_info.global_scope.symbols_in_frame)

# %%
import ast
import ast_scope
tree = ast.parse(code)
scope_info = ast_scope.annotate(tree)
graph = scope_info.static_dependency_graph
# %%
# %%
%matplotlib inline
# %%
scope_info.

# %%
import ast, ast_scope
tree = ast.parse(code)
tree.body[0]
# %%
