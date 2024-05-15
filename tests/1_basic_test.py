def test_number_input():
    sleep(0)
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
"""
        )
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        checkbox = page.locator("input[type=checkbox]")
        checkbox.check()
        sleep(2)
        assert "True" in page.inner_text("body")
        browser.close()
