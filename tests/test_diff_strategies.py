"""
End-to-end tests for content update (diff) strategies.

This module tests that the correct diff strategies are applied when users
interact with hstream components, triggering different types of DOM updates.
"""
import platform
from time import sleep
from playwright.sync_api import sync_playwright
from .conftest import write_py_script, get_server_logs


def wait_for_server():
    """Wait for server to be ready on GitHub CI."""
    if not platform.system() == "Darwin":
        sleep(15)  # Increased wait time for CI


def setup_test_script(contents):
    """Helper to write test script and wait for server."""
    sleep(0)
    write_py_script(contents=contents)
    wait_for_server()


def verify_strategy_in_logs(expected_strategy):
    """
    Verify that the expected diff strategy was logged by the server.

    Args:
        expected_strategy: The strategy string to look for (e.g., "1_full_replace")
    """
    all_output = get_server_logs()
    strategy_log = f"[DIFF_STRATEGY] Selected strategy: {expected_strategy}"
    
    # Also check test log file as fallback
    try:
        with open('test_strategy_logs.txt', 'r') as f:
            file_output = f.read()
            all_output += "\n" + file_output
    except FileNotFoundError:
        pass
    
    assert (
        strategy_log in all_output
    ), f"Expected strategy '{expected_strategy}' not found in logs. Output:\n{all_output[-2000:]}"


def test_full_replace_strategy_on_initial_load():
    """
    Test that full replace strategy is used on initial page load.

    Strategy: 1_full_replace
    Trigger: First page load with no previous HTML
    """
    setup_test_script(
        contents="""
from hstream import hs
hs.markdown('# Initial Load')
hs.markdown('This is the first render')
"""
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)  # 60 second timeout for CI
        page.goto("http://127.0.0.1:9000/")
        sleep(5)

        # Verify correct strategy was selected
        verify_strategy_in_logs("1_full_replace")

        # Verify content is present (full replace happened)
        assert "Initial Load" in page.inner_text("body")
        assert "This is the first render" in page.inner_text("body")
        browser.close()


def test_nothing_strategy_when_no_change():
    """
    Test that nothing strategy is used when user action doesn't change output.

    Strategy: 2_nothing
    Trigger: Button click that doesn't change any displayed content
    """
    setup_test_script(
        contents="""
from hstream import hs

# State that doesn't affect output
clicked = hs.button('Click me (no visible change)')

hs.markdown('Static content that never changes')
hs.markdown('More static content')
"""
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)  # 60 second timeout for CI
        page.goto("http://127.0.0.1:9000/")
        sleep(5)

        initial_content = page.inner_text("body")

        # Click button but output remains the same
        button = page.locator('button:has-text("Click me")')
        button.click()
        sleep(2)

        # Verify correct strategy was selected
        verify_strategy_in_logs( "2_nothing")

        # Content should be identical (nothing strategy)
        assert page.inner_text("body") == initial_content
        browser.close()


def test_partial_replace_strategy_when_content_changes():
    """
    Test that partial replace strategy is used when existing content changes.

    Strategy: 3_partial_replace
    Trigger: Text input that updates existing markdown elements
    """
    setup_test_script(
        contents="""
from hstream import hs

text = hs.text_input('Enter text', default_value='original')

hs.markdown(f'You typed: {text}')
hs.markdown('This line stays the same')
"""
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)  # 60 second timeout for CI
        page.goto("http://127.0.0.1:9000/")
        sleep(5)

        assert "You typed: original" in page.inner_text("body")

        # Type new text - this should trigger partial replace
        text_input = page.locator("input[type=text]")
        text_input.fill("updated")
        text_input.press("Enter")
        sleep(2)

        # Verify correct strategy was selected
        verify_strategy_in_logs( "3_partial_replace")

        # Content should be updated (partial replace)
        assert "You typed: updated" in page.inner_text("body")
        assert "This line stays the same" in page.inner_text("body")
        browser.close()


def test_partial_replace_strategy_when_elements_removed():
    """
    Test that partial replace strategy is used when conditional elements are removed.

    Strategy: 3_partial_replace
    Trigger: Checkbox that controls visibility of elements (fewer elements shown)
    """
    setup_test_script(
        contents="""
from hstream import hs

show_extra = hs.checkbox('Show extra content', default_value=True)

hs.markdown('Line 1: Always visible')
hs.markdown('Line 2: Always visible')

if show_extra:
    hs.markdown('Line 3: Conditional')
    hs.markdown('Line 4: Conditional')
"""
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)  # 60 second timeout for CI
        page.goto("http://127.0.0.1:9000/")
        sleep(5)

        # Initially all 4 lines should be visible
        assert "Line 1: Always visible" in page.inner_text("body")
        assert "Line 3: Conditional" in page.inner_text("body")
        assert "Line 4: Conditional" in page.inner_text("body")

        # Uncheck to remove conditional elements (partial replace with fewer elements)
        checkbox = page.locator("input[type=checkbox]")
        checkbox.uncheck()
        # Wait for the page to update and focus on any input to trigger update
        page.wait_for_timeout(1000)
        try:
            text_input = page.locator("input[type=text]").first
            text_input.focus()  # Trigger update
        except:
            # If text input doesn't exist anymore, just trigger with a click elsewhere
            page.locator("body").click()
        sleep(3)

        # Verify correct strategy was selected
        verify_strategy_in_logs( "3_partial_replace")

        # Conditional lines should be gone
        assert "Line 1: Always visible" in page.inner_text("body")
        assert "Line 2: Always visible" in page.inner_text("body")
        assert "Line 3: Conditional" not in page.inner_text("body")
        browser.close()


def test_partial_append_strategy_when_elements_added():
    """
    Test that partial append strategy is used when new elements are added.

    Strategy: 4_partial_append
    Trigger: Checkbox that shows additional content at the end
    """
    setup_test_script(
        contents="""
from hstream import hs

show_more = hs.checkbox('Show more content', default_value=False)

hs.markdown('Line 1: Always here')
hs.markdown('Line 2: Always here')

if show_more:
    hs.markdown('Line 3: Newly added')
    hs.markdown('Line 4: Newly added')
"""
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)  # 60 second timeout for CI
        page.goto("http://127.0.0.1:9000/")
        sleep(5)

        # Initially only 2 lines
        assert "Line 1: Always here" in page.inner_text("body")
        assert "Line 2: Always here" in page.inner_text("body")
        assert "Line 3: Newly added" not in page.inner_text("body")

        # Check box to add new elements (partial append)
        checkbox = page.locator("input[type=checkbox]")
        checkbox.check()
        # Wait for the page to update and focus on any input to trigger update
        page.wait_for_timeout(1000)
        try:
            text_input = page.locator("input[type=text]").first
            text_input.focus()  # Trigger update
        except:
            # If text input doesn't exist anymore, just trigger with a click elsewhere
            page.locator("body").click()
        sleep(3)

        # Verify correct strategy was selected
        verify_strategy_in_logs( "4_partial_append")

        # New lines should be appended
        assert "Line 1: Always here" in page.inner_text("body")
        assert "Line 2: Always here" in page.inner_text("body")
        assert "Line 3: Newly added" in page.inner_text("body")
        assert "Line 4: Newly added" in page.inner_text("body")
        browser.close()


def test_partial_append_with_counter():
    """
    Test partial append strategy with a counter that adds items incrementally.

    Strategy: 4_partial_append
    Trigger: Button clicks that add new list items
    """
    setup_test_script(
        contents="""
from hstream import hs

if hs.button('Add item'):
    if 'count' not in hs.session_state:
        hs.session_state['count'] = 1
    else:
        hs.session_state['count'] += 1

count = hs.session_state.get('count', 0)

hs.markdown('## Item List')
for i in range(count):
    hs.markdown(f'- Item {i + 1}')
"""
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)  # 60 second timeout for CI
        page.goto("http://127.0.0.1:9000/")
        sleep(5)

        # Initially no items
        initial_text = page.inner_text("body")
        assert "Item 1" not in initial_text

        # Click to add first item
        button = page.locator('button:has-text("Add item")')
        button.click()
        sleep(2)
        assert "Item 1" in page.inner_text("body")

        # Click to add second item (partial append)
        button.click()
        sleep(2)

        # Verify correct strategy was selected for append
        verify_strategy_in_logs( "4_partial_append")

        assert "Item 1" in page.inner_text("body")
        assert "Item 2" in page.inner_text("body")

        # Click to add third item (partial append)
        button.click()
        sleep(2)
        assert "Item 1" in page.inner_text("body")
        assert "Item 2" in page.inner_text("body")
        assert "Item 3" in page.inner_text("body")
        browser.close()


def test_multiple_inputs_partial_replace():
    """
    Test partial replace with multiple interactive elements.

    Strategy: 3_partial_replace
    Trigger: Multiple inputs that change different parts of the content
    """
    setup_test_script(
        contents="""
from hstream import hs

name = hs.text_input('Name', default_value='Alice')
age = hs.number_input('Age', default_value=25)

hs.markdown(f'## User Profile')
hs.markdown(f'Name: {name}')
hs.markdown(f'Age: {age}')
hs.markdown(f'Status: Active')
"""
    )
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)  # 60 second timeout for CI
        page.goto("http://127.0.0.1:9000/")
        sleep(5)

        assert "Name: Alice" in page.inner_text("body")
        assert "Age: 25" in page.inner_text("body")

        # Change name (partial replace)
        text_input = page.locator("input[type=text]")
        text_input.fill("Bob")
        text_input.press("Enter")
        sleep(2)

        # Verify correct strategy was selected
        verify_strategy_in_logs( "3_partial_replace")

        assert "Name: Bob" in page.inner_text("body")
        assert "Age: 25" in page.inner_text("body")
        assert "Status: Active" in page.inner_text("body")

        # Change age (partial replace)
        number_input = page.locator("input[type=number]")
        number_input.fill("30")
        number_input.press("Enter")
        sleep(2)

        assert "Name: Bob" in page.inner_text("body")
        assert "Age: 30" in page.inner_text("body")
        browser.close()
