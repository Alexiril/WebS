from __future__ import annotations

from html.parser import HTMLParser
from os.path import exists
from typing import TYPE_CHECKING

import database
from exception import ServerException
from functions import getLangCode, getSiteTitle

if TYPE_CHECKING:
    from typing import Any

    from handler import Handler

class PythonUnwrapper(HTMLParser):
    result: str
    pythonGlobals: dict[Any, Any]
    echoed: list[str]
    values: dict[str, Any]
    handler: Handler

    def __init__(self) -> None:
        self.result = ""
        self.echoed = list()
        def echo(string: str) -> None:
            self.echoed.append(string)
        def load(string: str) -> str:
            with open(string) as f:
                return PythonUnwrapper().prepareHtml(self.values, f.read(), self.handler)
        def value(name: str) -> Any:
            return self.values.get(name)
        def handler() -> Handler:
            return self.handler
        self.pythonGlobals = {
            "echo": echo,
            "value": value,
            "load": load,
            "handler": handler
        }
        super().__init__(convert_charrefs=True)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.result += f"""<{tag}{" " if len(attrs) > 0 else ""}{" ".join(map(lambda x: f'{x[0]}="{x[1] if x[1] != None else ""}"', attrs))}>"""

    def handle_endtag(self, tag: str) -> None:
        self.result += f"""</{tag}>"""

    def handle_data(self, data: str) -> None:
        self.result += data
    
    def handle_decl(self, decl: str) -> None:
        self.result += f"<!{decl}>"

    def handle_comment(self, data: str) -> None:
        while "  " in data: data = data.replace("  ", " ")
        data = f"def dont_call_it_auto1397():{data}\n globals().update(locals())\ndont_call_it_auto1397()"
        self.echoed = list()
        exec(data, self.pythonGlobals)
        self.result += "".join(map(str, self.echoed))

    def handle_pi(self, data: str) -> None:
        self.result += f"""<?{data}>"""

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def prepareHtml(self, values: dict[str, Any], data: str, handler: Handler) -> str:
        self.result = ""
        self.handler = handler
        self.values = values
        self.feed(data)
        return self.result

def buildPage(handler: Handler, path: str) -> None:
    filename: str = "theme/base.html"
    htmlFileName: str = f"theme/{path.split('/')[-1].split('?')[0] if handler.responceCode == 200 else handler.responceCode}.html"
    if exists(htmlFileName):
        filename = htmlFileName
    values: dict[str, Any] = {
        "langCode": getLangCode(),
        "pageTitle": getSiteTitle(),
    }
    try:
        content: list[Any] = database.getPageFromDB(path)
        if content[5] != "":
            values["pageTitle"] = content[5] 
        values["pageContent"] = PythonUnwrapper().prepareHtml(values, content[2], handler)
    except ServerException as e:
        if filename == "theme/base.html":
            raise e
    with open(filename) as f:
        handler.responceContent += PythonUnwrapper().prepareHtml(values, f.read(), handler).encode()