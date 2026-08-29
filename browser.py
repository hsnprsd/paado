import queue
import threading
from concurrent.futures import Future

from playwright.sync_api import Browser, Playwright, sync_playwright

from config import Config


class BrowserSession:
    def __init__(self, config: Config):
        self._playwright: Playwright = sync_playwright().start()
        self.browser: Browser = self._playwright.chromium.launch(
            executable_path=config.chrome_path, headless=config.chrome_headless
        )
        self.page = self.browser.new_page()

    def do_navigate(self, url: str):
        self.page.goto(url, wait_until="networkidle")

    def do_read_html(self) -> str:
        return self.page.content()

    def do_click(self, selector: str):
        self.page.click(selector)

    def do_type(self, selector: str, text: str):
        self.page.fill(selector, text)

    def close(self):
        self.browser.close()
        self._playwright.stop()


class BrowserThread:
    def __init__(self, config: Config):
        self._jobs = queue.Queue()
        self._thread = threading.Thread(target=self._loop, args=(config,), daemon=True)
        self._thread.start()

    def _loop(self, config: Config):
        session = BrowserSession(config)
        while True:
            job = self._jobs.get()
            if job is None:
                session.close()
                return
            fn, fut = job
            try:
                fut.set_result(fn(session))
            except Exception as exc:
                fut.set_exception(exc)

    def __getattr__(self, name):
        def proxy(*args, **kwargs):
            fut = Future()
            self._jobs.put((lambda session: getattr(session, name)(*args, **kwargs), fut))
            return fut.result()
        return proxy

    def close(self):
        self._jobs.put(None)
        self._thread.join()
