from time import sleep
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from .conftest import write_py_script

load_dotenv()


def do_content_in_page(content):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000/")
        sleep(2)
        print(page.inner_text("body"))
        assert content in page.inner_text("body")
        browser.close()


def test_blank_page():
    write_py_script(contents="from hstream import hs \nhs.markdown('Hello world')")
    do_content_in_page(content="Hello world")


def test_button():
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
        page.goto("http://127.0.0.1:8000/")
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
        page.goto("http://127.0.0.1:8000/")
        text_input = page.locator("input")
        text_input.type("my text value")
        text_input.press("Enter")
        sleep(2)
        assert "my text value" in page.inner_text("body")
        browser.close()
