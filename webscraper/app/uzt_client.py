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
from app import settings
from selectolax.lexbor import LexborHTMLParser


class UZTClient(httpx.Client):
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
        self._next_url = ""
        # kwargs["proxies"] = "https://89.43.31.134:3128"
        kwargs["headers"] = self.load_headers(settings.HEADERS_PATH)
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.response = super().get(*args, **kwargs)
        self._asp_form_inputs = None
        return self.response

    def submit_asp_form(self, href):
        data = self.prepare_form_data(href)
        self.response = super().post(url=str(self.response.url), data=data)
        self._asp_form_inputs = None
        return self.response

    def prepare_form_data(self, href):
        event_target = self.get_event_target(href)
        link_data = {
            "__EVENTTARGET": event_target,
            "__EVENTARGUMENT": "",
            "__ASYNCPOST": "true",
            "ctl00$MasterScriptManager": f"ctl00$MainArea$UpdatePanel1| {event_target}",
        }
        data = self.asp_form_inputs
        data.update(link_data)
        return data

    def save_to_html(self, filename):
        """
        Warning: This method automatically calls get(self.next_url) when invoked.
        Therefore, if you want to obtain the URL of the job detail page,
        make sure to call this method only after retrieving the next URL.
        """
        if self.response:
            with open(filename, "w") as file:
                file.write(self.text)
            return {"status": f"The file has been successfully saved as {filename}"}
        return {
            "status": "No 'http.response' object available for saving. The file was not saved."
        }

    @property
    def _has_response(self):
        if not self.response:
            raise UZTClient.PropertyError

    @property
    def asp_form_inputs(self):
        if self._asp_form_inputs:
            return self._asp_form_inputs

        input_nodes = self.tree.css("#aspnetForm input")
        if input_nodes:
            self._asp_form_inputs = {
                node.attrs.get("name"): node.attrs.get("value")
                for node in input_nodes
                if node.attrs.get("name").startswith("__")
            }
        else:
            need_to_get = ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
            splited_text = self.text.split("|")
            self._asp_form_inputs = {
                item: splited_text[splited_text.index(item) + 1] for item in need_to_get
            }
        return self._asp_form_inputs

    @property
    def is_redirect(self):
        self._has_response
        return "pageRedirect" in self.response.text

    @property
    def next_url(self):
        if not self.is_redirect:
            return False
        text = self.response.text
        pattern = re.compile(r"([^\|]+)\|$")
        match = pattern.search(text)
        if match:
            right_url = url_unquote(match.group(1))
            self._next_url = f"{settings.BASE_URL}/{right_url}"
            return self._next_url
        return False

    @property
    def text(self):
        """
        Warning: This method automatically calls get(self.next_url) when invoked.
        Therefore, if you want to obtain the URL of the job detail page,
        make sure to call this method only after retrieving the next URL.
        """
        self._has_response
        if self.response.text and "pageRedirect" in self.response.text:
            self.get(self.next_url)

        return self.response.text

    @property
    def tree(self):
        """
        Warning: This method automatically calls get(self.next_url) when invoked.
        Therefore, if you want to obtain the URL of the job detail page,
        make sure to call this method only after retrieving the next URL.
        """
        self._has_response
        return LexborHTMLParser(self.text)

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