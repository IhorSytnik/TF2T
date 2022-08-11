import re

from selenium.webdriver.chrome import webdriver
import requests

from classes.requestMethod import RequestMethod
from helping.factories import Singleton
from settings import HEADERS


class RequestBuilder:
    def __init__(self):
        self.method = RequestMethod.GET
        self.url = None
        self.params = None
        self.data = None
        self.headers = HEADERS
        self.cookies = None
        self.files = None
        self.auth = None
        self.timeout = None
        self.allow_redirects = True
        self.proxies = None
        self.hooks = None
        self.stream = None
        self.verify = None
        self.cert = None
        self.json = None


class BrowserGET:
    def get(self, url):
        """Send a GET request to a url."""
        pass

    def get_page_source(self) -> str:
        """Get current web page's source code."""
        pass

    def get_current_url(self) -> str:
        """Get current web page's url."""
        pass

    def go_to_and_get_source_get(self, url) -> str:
        """Send a GET request to a url and return web page's source code."""
        pass

    def load_cookies(self, cookies):
        """Loads cookies to the browser."""
        pass

    def get_status_code(self):
        """Returns a status code for the current request."""
        pass

    def get_request_builder(self) -> RequestBuilder:
        return RequestBuilder()

    def quit(self):
        """Shuts down the browser (call at the end)."""
        pass


class SeleniumChromeWebDriverBrowser(BrowserGET):
    driver: webdriver.WebDriver

    def __init__(self):
        options = webdriver.Options()
        options.headless = True
        self.driver = webdriver.WebDriver(options=options)

    def get(self, url):
        return self.driver.get(url)

    def get_page_source(self):
        return self.driver.page_source

    def get_current_url(self):
        return self.driver.current_url

    def go_to_and_get_source_get(self, url):
        self.get(url)
        return self.get_page_source()

    def load_cookies(self, cookies):
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def get_status_code(self):
        pass

    def quit(self):
        self.driver.quit()


class RequestsSessionBrowser(BrowserGET, metaclass=Singleton):
    session: requests.Session
    response: requests.Response
    common_headers: dict

    def __init__(self, common_headers=HEADERS):
        self.session = requests.session()
        self.common_headers = common_headers
        self.websites = {}

    def request_with_prep(self, method: RequestMethod, url, **kwargs):
        return self.request(method, url, headers=self.common_headers, **kwargs)

    def get(self, url) -> requests.Response:
        return self.request_with_prep(RequestMethod.GET, url)

    def post(self, url) -> requests.Response:
        return self.request_with_prep(RequestMethod.POST, url)

    def request(self, method: RequestMethod, url, **kwargs) -> requests.Response:
        website = re.findall(r'^(https://[\w\-\.]+)/?.*$', url)[0]
        if website not in self.websites:
            self.websites[website] = 0
        self.websites[website] += 1

        self.response = self.session.request(method.name, url, **kwargs)
        self.response.raise_for_status()
        return self.response

    def get_page_source(self):
        return self.response.text

    def get_current_url(self):
        return self.response.url

    def go_to_and_get_source_get(self, url):
        return self.go_to_and_get_source(RequestMethod.GET, url)

    def go_to_and_get_source(self, method: RequestMethod, url):
        self.request_with_prep(method, url)
        return self.get_page_source()

    def load_cookies(self, cookies):
        for cookie in cookies:
            required_args = {
                'name': cookie.pop('name', None),
                'value': cookie.pop('value', None)
            }
            httpOnly = cookie.pop('httpOnly', None)
            expiry = cookie.pop('expiry', None)
            sameSite = cookie.pop('sameSite', None)
            my_cookie = requests.cookies.create_cookie(**required_args, **cookie)
            self.session.cookies.set_cookie(my_cookie)

    def get_status_code(self):
        return self.response.status_code

    def quit(self):
        pass


session = RequestsSessionBrowser()
