from .captcha_solver import CaptchaSolver
from .proxy_manager import ProxyManager
from .browser_emulator import BrowserEmulator

class Scraper:
    def __init__(self, use_proxies=True, use_headless=False):
        """
        Initialize the Scraper with proxy and headless browser support.
        :param use_proxies: Enable proxy rotation.
        :param use_headless: Enable headless browser for dynamic pages.
        """
        self.proxy_manager = ProxyManager() if use_proxies else None
        self.headless = BrowserEmulator() if use_headless else None
        self.captcha_solver = CaptchaSolver()

    def get(self, url):
        """
        Send a GET request to the target URL and handle responses dynamically.
        :param url: The target URL.
        :return: Page content or None if request fails.
        """
        try:
            if self.headless:
                print(f"Using headless browser for {url}...")
                return self.headless.get_page_source(url)

            proxy = self.proxy_manager.get_proxy() if self.proxy_manager else None
            print(f"Sending GET request to {url} with proxy: {proxy}")
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(
                url,
                headers=headers,
                proxies={"http": proxy, "https": proxy} if proxy else None,
            )
            response.raise_for_status()
            print(f"Response received (status {response.status_code})")
            return response.text
        except Exception as e:
            print(f"Error during scraping: {e}")
            return None
