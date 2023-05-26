import http.server
import options
from exception import ServerException, getInternalExceptionPage
import database
import os
import builder

class Handler(http.server.BaseHTTPRequestHandler):
    responceContent: bytes
    responceCode: int
    contentType: str

    def __init__(self, request, client_address, server) -> None:
        self.responceContent = bytes()
        self.responceCode = 200
        self.contentType = "application/octet-stream"
        super().__init__(request, client_address, server)
        
    def version_string(self) -> str:
        return f"{options.ServerName}"

    def doContent(self) -> None:
        try:
            if self.path.split("/")[1] == "shared":
                ext = self.path.split(".")[-1]
                if ext in options.mimeTypes:
                    self.contentType = options.mimeTypes[ext]
                correctPath = os.path.join(os.getcwd(), os.path.sep.join(self.path.split("/")).lstrip(os.path.sep))
                if not os.path.exists(correctPath):
                    raise ServerException(404, "Cannot find the shared object")
                with open(correctPath, "rb") as file:
                    self.responceContent = file.read()
                    return
            self.contentType = "text/html"
            builder.buildPage(self, database.getPageFromDB(self.path))
        except ServerException as e:
            self.responceException(e.code)
        except Exception as e:
            self.responceException(500)

    def responceException(self, code: int) -> None:
        self.responceCode = code
        self.contentType = "text/html"
        try:
            builder.buildPage(self, database.getPageFromDB(f"$exception{code}"))
        except Exception as e:
            reverseStack = None
            if e.__traceback__ != None:
                reverseStack = e.__traceback__
                while reverseStack.tb_next != None:
                    reverseStack = reverseStack.tb_next
                reverseStack = f"file: {reverseStack.tb_frame.f_code.co_filename.split(os.path.sep)[-1]}, index: ({reverseStack.tb_lineno}, {reverseStack.tb_lasti})"
            self.responceContent = getInternalExceptionPage(
                self.version_string(), super().version_string(), f"loading {code} error page <br>({e if len(e.args) > 0 else 'Exception'}{f': {reverseStack}' if reverseStack != None else ''})", self.path).encode()

    def do_GET(self):
        self.do_HEAD()
        try:
            self.wfile.write(self.responceContent)
        except Exception as e:
            self.wfile.write(getInternalExceptionPage(
                self.version_string(), super().version_string(), f"sending undefined data <br>({e})", self.path).encode())

    def do_HEAD(self):
        try:
            self.doContent()
            self.send_response_only(self.responceCode)
            self.send_header('server', self.version_string())
            self.send_header('date', self.date_time_string())
            self.send_header('content-type', self.contentType)
            if type(self.responceContent) == bytes:
                self.send_header('content-length', f'{len(self.responceContent)}')
            self.end_headers()
        except Exception as e:
            self.send_response_only(500, str(e))

    def do_POST(self):
        pass
