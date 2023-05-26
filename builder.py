from html.parser import HTMLParser
from functions import getLangCode, getSiteTitle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from handler import Handler
    from typing import Sequence, Any

class PythonUnwrapper(HTMLParser):
    result: str
    pythonGlobals: dict[Any, Any]
    echoed: list[str]
    values: dict[str, Any]

    def __init__(self) -> None:
        self.result = ""
        self.echoed = list()
        def echo(string: str) -> None:
            self.echoed.append(string)
        def load(string: str) -> str:
            with open(string) as f:
                return PythonUnwrapper().prepareHtml(self.values, f.read())
        def value(name: str) -> Any:
            return self.values.get(name)
        self.pythonGlobals = {
            "echo": echo,
            "value": value,
            "load": load
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
        self.result += "".join(self.echoed)

    def handle_pi(self, data: str) -> None:
        self.result += f"""<?{data}>"""

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def prepareHtml(self, values: dict[str, Any], data: str) -> str:
        self.result = ""
        self.values = values
        self.feed(data)
        return self.result

builder = PythonUnwrapper()

def buildPage(handler: Handler, content: Sequence[str]) -> None:
    values: dict[str, Any] = {
        "langCode": getLangCode(),
        "pageTitle": content[5] if content[5] != "" else getSiteTitle(),
        "pageContent": content[2]
    }
    filename = "theme/base.html"
    if handler.responceCode == 500:
        filename = "theme/500.html"
    with open(filename) as f:
        handler.responceContent += builder.prepareHtml(values, f.read()).encode()