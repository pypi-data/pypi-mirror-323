import random

class ProxyManager:
    def __init__(self):
        """
        Initialize the ProxyManager with a list of proxies.
        """
        self.proxies = [
            "http://username:password@proxy1.com:8080",
            "http://username:password@proxy2.com:8080",
        ]

    def get_proxy(self):
        """
        Return a random proxy from the list.
        :return: A proxy string or None if no proxies are available.
        """
        if not self.proxies:
            return None
        return random.choice(self.proxies)
