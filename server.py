import http.server
import ssl
import handler
import serverOptions
import mysql.connector

class WebServer(http.server.ThreadingHTTPServer):

    def __init__(self, activate: bool = True) -> None:
        server_address = (serverOptions.ServerHost, serverOptions.ServerPort)
        super().__init__(server_address, RequestHandlerClass=handler.Handler)
        serverOptions.SQLConnection = mysql.connector.connect(
            host=serverOptions.SQLHost,
            port=serverOptions.SQLPort,
            user=serverOptions.SQLUser,
            passwd=serverOptions.SQLPassword
        )
        if serverOptions.SQLConnection != None:
            with serverOptions.SQLConnection.cursor() as cursor:
                cursor.execute("show databases")
                fetched = cursor.fetchall()
                if fetched != None:
                    if not any(map(lambda x: x[0] == serverOptions.SQLDBName, fetched)):
                        cursor.execute(f"create database `{serverOptions.SQLDBName}`")
                        serverOptions.SQLConnection.commit()
                    cursor.execute(f"use `{serverOptions.SQLDBName}`")
                    serverOptions.SQLConnection.commit()
        self.check_database()
        if serverOptions.SSLCertificate != "" and serverOptions.SSLKey != "":
            self.socket = ssl.wrap_socket(
                self.socket,
                server_side = True,
                certfile = serverOptions.SSLCertificate,
                keyfile = serverOptions.SSLKey,
                ssl_version = ssl.PROTOCOL_TLS
                )
        if activate:
            self.serve_forever()
    
    def check_database(self) -> None:
        tables = ["web_users", "web_users_meta", "web_pages"]
        if serverOptions.SQLConnection != None:
            with serverOptions.SQLConnection.cursor() as cursor:
                cursor.execute("show tables")
                needCommit = False
                fetched = cursor.fetchall()
                if fetched != None:
                    for table in tables:
                        if not any(map(lambda x: x[0] == table, fetched)):
                            sql = self.get_create_table_sql(table)
                            for query in sql:
                                cursor.execute(query)
                                needCommit = True
                if needCommit:
                    serverOptions.SQLConnection.commit()
        else:
            raise RuntimeError("No database connection")
        
    def get_create_table_sql(self, name: str) -> list[str]:
        if name == "web_pages":
            return [
                """
                CREATE TABLE `web_pages` (
                    `id` int(11) NOT NULL,
                    `url` text NOT NULL,
                    `content` longtext DEFAULT NULL,
                    `status` varchar(20) NOT NULL,
                    `author` int(11) NOT NULL,
                    `name` text NOT NULL,
                    `time_created` timestamp NOT NULL DEFAULT current_timestamp()
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci""",
                """
                ALTER TABLE `web_pages`
                    ADD PRIMARY KEY (`id`),
                    ADD UNIQUE KEY `url` (`url`) USING HASH,
                    ADD KEY `status` (`status`),
                    ADD KEY `author` (`author`)
                """,
                """
                ALTER TABLE `web_pages`
                    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT
                """,
                """
                ALTER TABLE `web_pages`
                    ADD CONSTRAINT `web_pages_ibfk_1` FOREIGN KEY (`author`) REFERENCES `web_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
                """
            ]
        elif name == "web_users":
            return [
                """
                CREATE TABLE `web_users` (
                    `id` int(11) NOT NULL,
                    `login` mediumtext NOT NULL,
                    `pass_hash` mediumtext NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
                """,
                """
                ALTER TABLE `web_users`
                    ADD PRIMARY KEY (`id`) USING BTREE,
                    ADD UNIQUE KEY `login` (`login`) USING HASH;
                """,
                """
                ALTER TABLE `web_users`
                    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
                """
            ]
        elif name == "web_users_meta":
            return [
                """
                CREATE TABLE `web_users_meta` (
                    `id` int(11) NOT NULL,
                    `user_id` int(11) NOT NULL,
                    `meta_key` text NOT NULL,
                    `meta_value` text NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
                """,
                """
                ALTER TABLE `web_users_meta`
                    ADD PRIMARY KEY (`id`),
                    ADD KEY `user_id` (`user_id`);
                """,
                """
                ALTER TABLE `web_users_meta`
                    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
                """,
                """
                ALTER TABLE `web_users_meta`
                    ADD CONSTRAINT `web_users_meta_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `web_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
                """
            ]
        return []