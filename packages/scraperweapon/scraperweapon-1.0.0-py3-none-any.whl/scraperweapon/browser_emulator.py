from playwright.sync_api import sync_playwright

class BrowserEmulator:
    def get_page_source(self, url):
        """
        Fetch the full page source using a headless browser.
        :param url: The target URL.
        :return: HTML content of the page.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            content = page.content()
            browser.close()
            return content
