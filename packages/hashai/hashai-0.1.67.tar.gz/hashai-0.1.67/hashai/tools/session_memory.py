class SessionMemory:
    def __init__(self):
        self.browser = None
        self.page = None
        self.current_url = None

    def set_browser(self, browser):
        self.browser = browser

    def set_page(self, page):
        self.page = page

    def set_url(self, url):
        self.current_url = url

    def clear(self):
        if self.browser:
            self.browser.close()
        self.browser = None
        self.page = None
        self.current_url = None
