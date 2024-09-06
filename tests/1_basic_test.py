from time import sleep
from playwright.sync_api import sync_playwright
from .conftest import write_py_script
import platform


def do_content_in_page(content):
    with sync_playwright() as playwright:
        if not platform.system() == "Darwin":
            sleep(10)  # wait for github server to start
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        sleep(2)
        print(page.inner_text("body"))
        assert content in page.inner_text("body")
        browser.close()


def test_blank_page():
    sleep(0)
    write_py_script(contents="from hstream import hs \nhs.markdown('Hello world')")
    do_content_in_page(content="Hello world")


def test_button():
    sleep(0)
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
hs.markdown('Hello world')
if hs.button('Press me'):
    hs.markdown('pressed')
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        assert "pressed" not in page.inner_text("body")
        button = page.locator('button:has-text("Press me")')
        print(button)
        # from ipdb import set_trace; set_trace()
        button.click()
        print(page.inner_text("body"))
        sleep(2)
        print(page.inner_text("body"))
        sleep(2)
        assert "pressed" in page.inner_text("body")
        browser.close()


def test_text():
    sleep(0)
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
text = hs.text_input('Enter text')
hs.markdown(text)
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        text_input = page.locator("input")
        text_input.type("my text value")
        text_input.press("Enter")
        sleep(2)
        assert "my text value" in page.inner_text("body")
        browser.close()


def test_number_input():
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
number = hs.number_input('Enter number', default_value=5)
hs.markdown(str(number))
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        number_input = page.locator("input[type=number]")
        number_input.fill("10")
        number_input.press("Enter")
        sleep(2)
        assert "10" in page.inner_text("body")
        browser.close()


def test_select_box():
    sleep(0)
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
option = hs.select_box(['Option 1', 'Option 2', 'Option 3'], default_value='Option 1')
hs.markdown(option)
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        select_box = page.locator("select")
        select_box.select_option("Option 2")
        sleep(2)
        assert "Option 2" in page.inner_text("body")
        browser.close()


def test_checkbox():
    sleep(0)
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
checked = hs.checkbox('Check me', default_value=False)
hs.markdown(str(checked))
hs.text_input('text')
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        checkbox = page.locator("input[type=checkbox]")
        checkbox.check()
        text = page.locator("input[type=text]")
        text.focus()
        sleep(2)
        assert "True" in page.inner_text("body")
        browser.close()

def test_sl_button():
    sleep(0)
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
if hs.sl_button('Click me', variant='primary'):
    hs.markdown('Button clicked!')
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        button = page.locator('sl-button:has-text("Click me")')
        assert button.get_attribute('variant') == 'primary'
        assert "Button clicked!" not in page.inner_text("body")
        button.click()
        sleep(2)
        assert "Button clicked!" in page.inner_text("body")
        browser.close()

def test_sl_input():
    sleep(0)
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
text = hs.sl_input('Enter text', placeholder='Type here')
hs.markdown(text)
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        input_field = page.locator("sl-input")
        assert input_field.get_attribute('placeholder') == 'Type here'
        input_field.fill("Hello, Shoelace!")
        input_field.press("Enter")
        sleep(2)
        assert "Hello, Shoelace!" in page.inner_text("body")
        browser.close()

def test_sl_format_date():
    sleep(0)
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
hs.sl_format_date('2023-05-15', month='long', day='numeric', year='numeric')
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        formatted_date = page.locator("sl-format-date")
        sleep(2)
        assert "May 15, 2023" in page.inner_text("body")
        browser.close()

def test_sl_multiselect():
    sleep(0)
    with sync_playwright() as playwright:
        write_py_script(
            contents="""
from hstream import hs
options = ['Apple', 'Banana', 'Cherry']
selected = hs.sl_multiselect(options, default_value=['Apple'])
hs.markdown(str(selected))
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        multiselect = page.locator("sl-select")
        assert "Apple" in multiselect.inner_text()
        multiselect.click()
        page.locator("sl-option", has_text="Cherry").click()
        page.keyboard.press("Escape")
        sleep(2)
        assert "['Apple', 'Cherry']" in page.inner_text("body")
        browser.close()
