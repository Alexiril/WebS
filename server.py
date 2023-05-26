import http.server
import ssl
import handler
import options
import mysql.connector
import database

class WebServer(http.server.ThreadingHTTPServer):

    def __init__(self, activate: bool = True) -> None:
        server_address = (options.ServerHost, options.ServerPort)
        super().__init__(server_address, RequestHandlerClass=handler.Handler)
        options.SQLConnection = mysql.connector.connect(
            host=options.SQLHost,
            port=options.SQLPort,
            user=options.SQLUser,
            passwd=options.SQLPassword
        )
        if options.SQLConnection != None:
            with options.SQLConnection.cursor() as cursor:
                cursor.execute("show databases")
                fetched = cursor.fetchall()
                if fetched != None:
                    if not any(map(lambda x: x[0] == options.SQLDBName, fetched)):
                        cursor.execute(f"create database `{options.SQLDBName}`")
                        options.SQLConnection.commit()
                    cursor.execute(f"use `{options.SQLDBName}`")
                    options.SQLConnection.commit()
        database.checkTables()
        if options.SSLCertificate != "" and options.SSLKey != "":
            self.socket = ssl.wrap_socket(
                self.socket,
                server_side = True,
                certfile = options.SSLCertificate,
                keyfile = options.SSLKey,
                ssl_version = ssl.PROTOCOL_TLS
                )
        if activate:
            self.serve_forever()