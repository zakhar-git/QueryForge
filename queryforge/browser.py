import webbrowser


class Browser:
    def open(self, url: str) -> bool:
        try:
            return bool(webbrowser.open_new_tab(url))
        except webbrowser.Error:
            return False

    def open_many(self, urls: list[str]) -> int:
        opened = 0
        for url in urls[:10]:
            if self.open(url):
                opened += 1
        return opened
