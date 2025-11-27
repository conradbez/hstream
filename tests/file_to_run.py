
from hstream import hs

show_more = hs.checkbox('Show more content', default_value=False)

hs.markdown('Line 1: Always here')
hs.markdown('Line 2: Always here')

if show_more:
    hs.markdown('Line 3: Newly added')
    hs.markdown('Line 4: Newly added')
