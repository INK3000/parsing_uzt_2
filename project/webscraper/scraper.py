# проверить есть ли в таблице катогории записи
# если нет
#   получить названия, ссылки, сформировать список, сериализовать и отправить запрос api на создание категорий
#
# получить список категорий из базы
#
# для каждой категории
#  зайти в категорию, собрать вакансии на странице, добавить в список
#  проверить, есть ли еще страницы в категории - если да, получить ссылку и перейти на следующую страницу, повторить цикл
#  если больше страниц нет, сериализировать данные и отправить в API
#
#  получить id последнего добавленного элемента, отправить в api запрос на обновление категории
import httpx
from selectolax.lexbor import LexborHTMLParser


class Scraper(httpx.Client):
    # Custom exception
    class PropertyError(Exception):
        def __init__(self):
            self.message = "Before use this property, need to call get(url) method"
            super().__init__(self.message)

    # Scraper class's methods and properties
    def __init__(self, *args, **kwargs):
        self.response: httpx.Response | None = None
        self._asp_form_inputs: dict | None = None
        self._asp_form_onsubmit_url: str | None = None
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.response = super().get(*args, **kwargs)
        self._asp_form_inputs = None
        self._asp_form_onsubmit_url = None
        return self.response

    def submit_asp_form(self, event_target, event_argument=""):
        self.asp_form_inputs.update({"__EVENTTARGET": event_target})
        self.asp_form_inputs.update({"__EVENTARGUMENT": event_argument})

    @property
    def tree(self):
        if self.response:
            return LexborHTMLParser(self.response.text)
        else:
            raise Scraper.PropertyError

    @property
    def asp_form_inputs(self):
        if not self._asp_form_inputs:
            input_nodes = self.tree.css("#aspnetForm input")
            if input_nodes:
                self._asp_form_inputs = {
                    node.attrs.get("name"): node.attrs.get("value")
                    for node in input_nodes
                    if node.attrs.get("name").startswith("__")
                }
        return self._asp_form_inputs

    # refactor to property
    def get_asp_form_onsubmit_url(self):
        asp_form_onsubmit_url = None

        return asp_form_onsubmit_url

    @staticmethod
    def load_headers(filename: str) -> dict:
        with open(filename, "r") as file:
            pattern = re.compile(r"^(.*): (.*)")
            headers = dict()
            for line in file:
                m = re.match(pattern, line)
                if len(m.groups()) == 2:
                    key, value = m.groups()
                    headers[key] = value
        return headers
