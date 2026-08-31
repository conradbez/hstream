"""Basic coverage for components that had none: file_upload, pyplot, dataframes,
multiselect and nav.

Two conventions here differ from `1_basic_test.py` on purpose:

* Assertions are scoped to the element under test rather than matched as a
  substring of the whole ``body``. A body-wide ``in`` check can be satisfied by
  unrelated markup - ``test_select_box`` passes without ever selecting anything,
  because every ``<option>`` label is in ``body`` from the start.
* Waiting is done with Playwright's auto-retrying ``expect`` instead of a fixed
  ``sleep``, so a slow rerun makes the suite slower rather than red.

``xfail`` marks record bugs that exist today. They are strict, so fixing the
underlying bug turns the test red and prompts you to drop the mark.
"""

import platform
from contextlib import contextmanager
from pathlib import Path
from time import sleep

import pytest
from playwright.sync_api import expect, sync_playwright

from .conftest import write_py_script

# A rerun has to round-trip the script, so give assertions room on slow runners.
TIMEOUT = 20_000


@contextmanager
def rendered(script):
    """Serve ``script`` through the session server and yield a loaded page."""
    write_py_script(contents=script)
    with sync_playwright() as playwright:
        if platform.system() != "Darwin":
            sleep(10)  # wait for the github runner's server to come up
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:9000/")
        # Rewriting file_to_run.py trips Django's StatReloader, so a load can land
        # mid-restart and render nothing. Reload once before giving up.
        # Wait on a child element rather than text - a plot-only page has no text.
        content = page.locator("#hs-content > *").first
        try:
            expect(content).to_be_attached(timeout=TIMEOUT)
        except AssertionError:
            page.reload()
            expect(content).to_be_attached(timeout=TIMEOUT)
        try:
            yield page
        finally:
            browser.close()


def test_file_upload_renders_input():
    with rendered(
        """
from hstream import hs
name = hs.file_upload('Pick a file', accept='.txt')
hs.markdown(f'FILE={name}')
"""
    ) as page:
        file_input = page.locator("#hs-content input[type=file]")
        expect(file_input).to_have_count(1, timeout=TIMEOUT)
        expect(file_input).to_have_attribute("accept", ".txt")
        # No upload yet, so the script sees None.
        expect(page.locator("#hs-content")).to_contain_text(
            "FILE=None", timeout=TIMEOUT
        )


def test_file_upload_round_trips_filename(tmp_path):
    # Distinctive name: the server copies uploads into ./tmp/, which is a real
    # (and version-controlled) directory, so this must not collide with a file
    # someone actually keeps there.
    upload = tmp_path / "hstream_test_upload.txt"
    upload.write_text("hello test file")
    server_copy = Path("./tmp") / upload.name

    try:
        with rendered(
            """
from hstream import hs
name = hs.file_upload('Pick a file', accept='.txt')
hs.markdown(f'FILE={name}')
"""
        ) as page:
            page.locator("#hs-content input[type=file]").set_input_files(str(upload))

            content = page.locator("#hs-content")
            # The component swaps the input out for the filename plus a Remove button.
            expect(content).to_contain_text(
                f"Current file: {upload.name}", timeout=TIMEOUT
            )
            expect(page.locator("#hs-content button:has-text('Remove')")).to_have_count(
                1
            )
            # And the script itself receives the filename as the component's value.
            expect(content).to_contain_text(f"FILE={upload.name}", timeout=TIMEOUT)
    finally:
        # Don't leave the uploaded copy behind as an untracked repo file.
        server_copy.unlink(missing_ok=True)


def test_pyplot_renders_png_data_uri():
    with rendered(
        """
from hstream import hs
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([0, 1, 2], [0, 1, 4])
hs.pyplot(fig, key='myplot')
"""
    ) as page:
        img = page.locator("#hs-content img")
        expect(img).to_have_count(1, timeout=TIMEOUT)

        src = img.get_attribute("src")
        assert src.startswith("data:image/png;base64,")
        # Guard against an empty or placeholder image being reported as success.
        assert len(src) > 1000, f"plot data URI implausibly short: {len(src)} chars"


def test_write_dataframe_renders_table():
    with rendered(
        """
from hstream import hs
import pandas as pd
hs.write_dataframe(pd.DataFrame({'alpha': [1, 2], 'beta': [3, 4]}))
"""
    ) as page:
        table = page.locator("#hs-content table")
        expect(table).to_have_count(1, timeout=TIMEOUT)

        # Column headers, by position, so a stray match elsewhere can't pass this.
        headers = table.locator("thead th")
        expect(headers.nth(1)).to_have_text("alpha")
        expect(headers.nth(2)).to_have_text("beta")

        expect(table.locator("tbody tr")).to_have_count(2)
        first_row = table.locator("tbody tr").nth(0).locator("td")
        expect(first_row.nth(0)).to_have_text("1")
        expect(first_row.nth(1)).to_have_text("3")


def test_multiselect_renders_all_options():
    with rendered(
        """
from hstream import hs
selected = hs.multiselect(['Red', 'Green', 'Blue'], default_value=[])
hs.markdown(f'SELECTED={selected}')
"""
    ) as page:
        boxes = page.locator("#hs-content input[type=checkbox]")
        expect(boxes).to_have_count(3, timeout=TIMEOUT)
        for option in ("Red", "Green", "Blue"):
            expect(
                page.locator(f"#hs-content input[type=checkbox][value='{option}']")
            ).to_have_count(1)
        # Nothing selected yet.
        expect(page.locator("#hs-content")).to_contain_text(
            "SELECTED=[]", timeout=TIMEOUT
        )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "multiselect submit is broken: its checkboxes are named per-option, but "
        "views.py reads request.POST['new_value'], so the stored value is None and "
        "the component's `for v in kwargs['value']` raises "
        "\"'NoneType' object is not iterable\". Drop this mark once it round-trips."
    ),
)
def test_multiselect_submit_round_trips_selection():
    with rendered(
        """
from hstream import hs
selected = hs.multiselect(['Red', 'Green', 'Blue'], default_value=[])
hs.markdown(f'SELECTED={selected}')
"""
    ) as page:
        page.locator("#hs-content summary").click()
        page.locator("#hs-content input[type=checkbox][value='Green']").check()
        page.locator("#hs-content button[type=submit]").click()

        # Assert on the script's own output marker, not the bare word "Green" -
        # that appears in the checkbox labels whether or not the submit worked.
        expect(page.locator("#hs-content")).to_contain_text(
            "SELECTED=['Green']", timeout=TIMEOUT
        )


def test_nav_renders_items():
    with rendered(
        """
from hstream import hs
page = hs.nav(['Home', 'About'])
hs.markdown(f'PAGE={page}')
"""
    ) as page:
        items = page.locator("nav li a")
        expect(items).to_have_count(2, timeout=TIMEOUT)
        expect(items.nth(0)).to_have_text("Home")
        expect(items.nth(1)).to_have_text("About")

        # Each item posts its own label back as the component's value.
        hx_post = page.locator("nav li").nth(1).get_attribute("hx-post")
        assert "new_value=About" in hx_post, hx_post


@pytest.mark.xfail(
    strict=True,
    reason=(
        "nav never reaches the user: its relocation into #hs-nav is driven by a "
        "hyperscript `on load` handler, but hyperscript 0.9.13 processes neither "
        "htmx-inserted nodes (no MutationObserver, no htmx.onLoad hook), so the "
        "header keeps its initial style=display:none inside #hs-content. Confirmed "
        "under htmx 2 + idiomorph too, so this predates the htmx 4 migration."
    ),
)
def test_nav_is_visible_to_the_user():
    with rendered(
        """
from hstream import hs
page = hs.nav(['Home', 'About'])
hs.markdown(f'PAGE={page}')
"""
    ) as page:
        expect(page.locator("#hs-nav nav")).to_have_count(1, timeout=TIMEOUT)
        expect(page.locator("#nav-content")).to_be_visible()
