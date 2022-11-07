from hyperstream import hs
from yattag import Doc

nav_from_user = hs.nav(label = [i for i in range(20)], default_value='1', key = 'nav1')

# sine_height = hs.text_input(text = 'Sine height', default_value='3', key = 'myinput')

hs.text_input('test','test' , key = 'test123')
hs.markdown('''# test''', key = 'testmarkdown')

hs.write(nav_from_user, key='123')

if int(nav_from_user) > 5:
    hs.write('nav_from_user greater than 50', key='output')