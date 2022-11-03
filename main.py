from hyperstream import Hyperstream as hs
hs = Hyperstream(clean_reload=False)

text_entered = hs.text_input(text = 'text_input_label', default_value='default_value', key = 'myinput')
hs.write(text_entered, key = 'mywrite')
hs.write(text_entered+'2', key = 'mywrite2')
print(text_entered, 'in main.py')