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
import re
from urllib.parse import unquote as url_unquote

import httpx
from selectolax.lexbor import LexborHTMLParser


class UZTScraper(httpx.Client):
    """
    The class extends the Client class and provides an additional feature:
    after loading a page using the GET method, you can follow URLs like:
    javascript:__doPostBack('ctl00$MainArea$GroupedPOSearchTab$ProffessionGroups$ctl00$ProfGroup',')

    Also, after following the URLs property 'tree' returns
    an object of class selectolax.LexborHTMLParser
    which can be used for parsing html.

    Example:
        uzt = UZTScraper()
        uzt.get(url="https://portal.uzt.lt/LDBPortal/Pages/ServicesForEmployees.aspx")
        uzt.submit_asp_form("javascript:__doPostBack('ctl00$MainArea$GroupedPOSearchTab$ProffessionGroups$ctl00$ProfGroup','')")
        tree = uzt.tree
        li_list = uzt.tree.css("#ctl00_MainArea_UpdatePanel1 li")

    """

    # Custom exception
    class PropertyError(Exception):
        def __init__(self):
            self.message = (
                "Before using this property, you need to call the get(url) method"
            )
            super().__init__(self.message)

    # Scraper class's methods and properties
    def __init__(self, *args, **kwargs):
        self.response: httpx.Response | None = None
        self._asp_form_inputs: dict | None = None
        kwargs["headers"] = self.load_headers("webscraper/headers.txt")
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.response = super().get(*args, **kwargs)
        self._asp_form_inputs = None
        return self.response

    # ToDo --------------------------------------------------
    def submit_asp_form(self, href):
        event_target = self.get_event_target(href)
        link_data = {
            "__EVENTTARGET": event_target,
            "__EVENTARGUMENT": "",
            "__ASYNCPOST": "true",
            "ctl00$MasterScriptManager": f"ctl00$MainArea$UpdatePanel1| {event_target}",
        }
        data = self.asp_form_inputs
        data.update(link_data)

        self.response = super().post(
            url=str(self.response.url), data=data  # , follow_redirects=True
        )
        return self.response

    @property
    def text(self):
        if not self.response:
            raise UZTScraper.PropertyError

        if self.response.text and "pageRedirect" in self.response.text:
            self.get(self.get_redirect_url(self.response.text))

        return self.response.text

    @property
    def tree(self):
        if not self.response:
            raise UZTScraper.PropertyError
        return LexborHTMLParser(self.text)

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

    @staticmethod
    def get_redirect_url(text):
        pattern = re.compile(r"([^\|]+)\|$")
        match = pattern.search(text)
        if match:
            right_url = url_unquote(match.group(0))
            redirect_url = f"https://portal.uzt.lt/{right_url}"
            return redirect_url
        raise Exception(
            "It is not possible to obtain the redirect_url from the provided {text}"
        )

    @staticmethod
    def get_event_target(href: str) -> str | bool:
        pattern = re.compile(r"\('(.+)',''\)")
        match = pattern.search(href)
        if match:
            result = match.group(1)
            return result
        else:
            raise Exception(
                f"It is not possible to obtain the event_target from the provided {href}"
            )

    def save_to_html(self, filename):
        if self.response:
            with open(filename, "w") as file:
                file.write(self.text)
            return {"status": f"The file has been successfully saved as {filename}"}
        return {
            "status": "No 'http.response' object available for saving. The file was not saved."
        }
