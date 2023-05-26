import time

class ServerException(Exception):

    code: int

    def __init__(self, code: int, *args: object) -> None:
        self.code = code
        super().__init__(*args)


def getInternalExceptionPage(serverName: str, serverVersion: str, reason: str, path: str) -> str:
    year, month, day, hh, mm, ss, _, _, _ = time.localtime()
    actualTime = "%02d/%02d/%04d %02d:%02d:%02d" % (day, month, year, hh, mm, ss)
    return f"""<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>{serverName} - Internal error</title>
                    <style>
                        .errorDiv {{
                            text-align: center;
                            margin-top: 5em;
                            font-family: monospace;
                        }}
                        .errorDivCenter {{
                            width: 50%;
                            margin: auto;
                            box-shadow: 0 0 20px -15px black;
                            padding: 3em;
                        }}
                        svg {{
                            width: 25%;
                        }}
                        hr {{
                            height: 0.2em;
                            background-color: #000000cc;
                            border: none;
                            width: 80%;
                        }}
                    </style>
                </head>
                <body>
                    <div class="errorDiv">
                        <div class="errorDivCenter">
                            <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" viewBox="0 0 256 256" xml:space="preserve">
                                <defs>
                                </defs>
                                <g style="stroke: none; stroke-width: 0; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: none; fill-rule: nonzero; opacity: 1;"
                                    transform="translate(1.4065934065934016 1.4065934065934016) scale(2.81 2.81)">
                                    <path
                                        d="M 85.429 85.078 H 4.571 c -1.832 0 -3.471 -0.947 -4.387 -2.533 c -0.916 -1.586 -0.916 -3.479 0 -5.065 L 40.613 7.455 C 41.529 5.869 43.169 4.922 45 4.922 c 0 0 0 0 0 0 c 1.832 0 3.471 0.947 4.386 2.533 l 40.429 70.025 c 0.916 1.586 0.916 3.479 0.001 5.065 C 88.901 84.131 87.261 85.078 85.429 85.078 z M 45 7.922 c -0.747 0 -1.416 0.386 -1.79 1.033 L 2.782 78.979 c -0.373 0.646 -0.373 1.419 0 2.065 c 0.374 0.647 1.042 1.033 1.789 1.033 h 80.858 c 0.747 0 1.416 -0.387 1.789 -1.033 s 0.373 -1.419 0 -2.065 L 46.789 8.955 C 46.416 8.308 45.747 7.922 45 7.922 L 45 7.922 z M 45 75.325 c -4.105 0 -7.446 -3.34 -7.446 -7.445 s 3.34 -7.445 7.446 -7.445 s 7.445 3.34 7.445 7.445 S 49.106 75.325 45 75.325 z M 45 63.435 c -2.451 0 -4.446 1.994 -4.446 4.445 s 1.995 4.445 4.446 4.445 s 4.445 -1.994 4.445 -4.445 S 47.451 63.435 45 63.435 z M 45 57.146 c -3.794 0 -6.882 -3.087 -6.882 -6.882 V 34.121 c 0 -3.794 3.087 -6.882 6.882 -6.882 c 3.794 0 6.881 3.087 6.881 6.882 v 16.144 C 51.881 54.06 48.794 57.146 45 57.146 z M 45 30.239 c -2.141 0 -3.882 1.741 -3.882 3.882 v 16.144 c 0 2.141 1.741 3.882 3.882 3.882 c 2.14 0 3.881 -1.741 3.881 -3.882 V 34.121 C 48.881 31.98 47.14 30.239 45 30.239 z"
                                        style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: rgb(255,155,0); fill-rule: nonzero; opacity: 1;"
                                        transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round" />
                                </g>
                            </svg>
                            <h2>{serverName} - Internal error has happened</h2>
                            <hr>
                            <h3>Server error</h3>
                            <h4>Server {serverName} - {serverVersion}</h4>
                            <p>URL: {path}</p>
                            <p>Timestamp: {actualTime}</p>
                            <p>Service failed due to {reason}</p>
                        </div>
                    </div>
                </body>
                </html>"""