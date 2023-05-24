import http.server
import serverOptions
import internal500

class Handler(http.server.BaseHTTPRequestHandler):
    responseContent: bytes

    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server)
        self.responseContent = bytes()

    def version_string(self) -> str:
        return f"{serverOptions.ServerName}"

    def do_Content(self):
        self.responseContent = "Hei!".encode()

    def responce_Exception(self, code: int):
        try:
            raise Exception()
            # TODO: Here goes a sql query to db to get the error page
            self.responseContent = "Oopsies".encode()
        except:
            self.responseContent = internal500.get_page(self.version_string(), super().version_string()).encode()

    def do_Headers(self):
        try:
            self.do_Content()
            raise Exception()
            self.send_response_only(200)
            self.send_header('server', self.version_string())
            self.send_header('date', self.date_time_string())
            self.send_header('content-type','text/html')
            self.send_header('content-length', f'{len(self.responseContent)}')
            self.end_headers()
        except:
            self.responce_Exception(500)
            self.send_response_only(500)
            self.send_header('server', self.version_string())
            self.send_header('date', self.date_time_string())
            self.send_header('content-type','text/html')
            self.send_header('content-length', f'{len(self.responseContent)}')
            self.end_headers()

    def do_GET(self):
        self.do_Headers()
        self.wfile.write(self.responseContent)

    def do_POST(self):
        pass

    def do_HEAD(self):
        self.do_Headers()