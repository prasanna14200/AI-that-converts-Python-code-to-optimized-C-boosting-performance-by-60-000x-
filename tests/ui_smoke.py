import json
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(accept_downloads=True)
        context.grant_permissions(["clipboard-read", "clipboard-write"], origin="http://127.0.0.1:5000")
        page = context.new_page()

        def convert_stub(route):
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "cpp_code": "#include <iostream>\nint main(){ std::cout << 10 << std::endl; return 0; }\n",
                        "model": "ui-smoke-test",
                        "provider": "test-double",
                        "direction": "Python to C++",
                    }
                ),
            )

        page.route("**/api/convert", convert_stub)
        page.goto("http://127.0.0.1:5000/", wait_until="networkidle")
        page.locator("#source").fill("total = 0\nfor i in range(5):\n    total += i\nprint(total)\n")
        page.locator("#convert").click()
        page.wait_for_function("document.querySelector('#output').value.includes('#include <iostream>')")

        page.locator("#copy").click()
        copied = page.evaluate("navigator.clipboard.readText()")
        if "#include <iostream>" not in copied:
            raise AssertionError("Copy button did not place generated C++ on the clipboard.")

        with tempfile.TemporaryDirectory() as tmp:
            with page.expect_download() as download_info:
                page.locator("#download").click()
            download = download_info.value
            target = Path(tmp) / download.suggested_filename
            download.save_as(target)
            if "#include <iostream>" not in target.read_text(encoding="utf-8"):
                raise AssertionError("Downloaded file did not contain generated C++.")

        browser.close()
        print("UI smoke passed: enter, convert, inspect, copy, and download.")


if __name__ == "__main__":
    main()
