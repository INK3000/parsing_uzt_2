import re
from urllib.parse import unquote, urljoin

import httpx
from selectolax.lexbor import LexborHTMLParser

from .settings import settings


class UZTClient(httpx.Client):
    """
    The class extends the httpx.Client class and provides an additional feature:
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
            self.message = 'Before using this property, you need to call the get(url) method'
            super().__init__(self.message)

    class AspInputsError(Exception):
        def __iniy__(self):
            self.message = 'It is not possible to get asp_form_inputs.'
            super().__init__(self.message)

    # Scraper class's methods and properties
    def __init__(self, *args, **kwargs):
        self.response: httpx.Response | None = None
        self.redirect_response: httpx.Response | None = None
        self._asp_form_inputs: dict | None = None
        self.only_url = False
        # kwargs["proxies"] = "http://37.27.3.22:8080"
        kwargs['headers'] = settings.target.headers
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.response = super().get(*args, **kwargs)
        self._asp_form_inputs = None
        self.redirect_response = None
        return self.response

    def submit_asp_form(self, href, only_url=False):
        self.only_url = only_url
        data = self.prepare_form_data(href)
        response = super().post(url=str(self.response.url), data=data)
        if 'pageRedirect' in response.text:
            self.redirect_response = response
        else:
            self.response = response
            self.redirect_response = None
            self._asp_form_inputs = None
        return response

    def prepare_form_data(self, href):
        event_target = self.get_event_target(href)
        link_data = {
            '__EVENTTARGET': event_target,
            '__EVENTARGUMENT': '',
            '__ASYNCPOST': 'true',
            'ctl00$MasterScriptManager': f'ctl00$MainArea$UpdatePanel1| {event_target}',
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
            with open(filename, 'w') as file:
                file.write(self.text)
            return {
                'status': f'The file has been successfully saved as {filename}'
            }
        return {
            'status': "No 'http.response' object available for saving. The file was not saved."
        }

    @property
    def _has_response(self):
        if not (self.response or self.redirect_response):
            raise UZTClient.PropertyError

    @property
    def asp_form_inputs(self):
        """
        returns current page's inputs for aspnetForm
        """
        if self._asp_form_inputs:
            return self._asp_form_inputs

        input_nodes = self.tree.css('#aspnetForm input')
        if input_nodes:
            self._asp_form_inputs = {
                node.attrs.get('name'): node.attrs.get('value')
                for node in input_nodes
                if node.attrs.get('name').startswith('__')
            }
        else:
            try:
                need_to_get = (
                    '__VIEWSTATE',
                    '__VIEWSTATEGENERATOR',
                    '__EVENTVALIDATION',
                )
                splited_text = self.text.split('|')
                self._asp_form_inputs = {
                    item: splited_text[splited_text.index(item) + 1]
                    for item in need_to_get
                }
            except Exception:
                raise UZTClient.AspInputsError
        return self._asp_form_inputs

    @property
    def next_url(self):
        """
        returns url to redirect if page has been redirected
        """
        if not self.redirect_response:
            return False
        text = self.redirect_response.text
        pattern = re.compile(r'([^\|]+)\|$')
        re_match = pattern.search(text)
        if re_match:
            right_url = unquote(re_match.group(1))
            next_url = urljoin(settings.target.base_url, right_url)
            return next_url
        return False

    @property
    def text(self):
        """
        Warning: This method automatically calls get(self.next_url) when invoked.
        Therefore, if you want to obtain the URL of the job detail page,
        make sure to call this method only after retrieving the next URL.
        """
        self._has_response

        if self.redirect_response and not self.only_url:
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
    def get_event_target(href: str) -> str | bool:
        pattern = re.compile(r"\('(.+)',''\)")
        re_match = pattern.search(href)
        if re_match:
            result = re_match.group(1)
            return result
        else:
            raise Exception(
                f'It is not possible to obtain the event_target from the provided {href}'
            )
