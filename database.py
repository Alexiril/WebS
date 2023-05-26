import options
from exception import ServerException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

def getPageFromDB(pageURL: str) -> list[Any]:
    if options.SQLConnection != None:
        with options.SQLConnection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM `web_pages` WHERE `url` = "{pageURL}"')
            fetched = cursor.fetchone()
            if fetched != None:
                return list(fetched)
            else:
                raise ServerException(404, "No object in the database")
    else:
        raise ServerException(500, "No database connection")


def checkTables():
    tables = ["web_users", "web_users_meta", "web_pages", "web_options"]
    if options.SQLConnection != None:
        with options.SQLConnection.cursor() as cursor:
            cursor.execute("show tables")
            needCommit = False
            fetched = cursor.fetchall()
            if fetched != None:
                for table in tables:
                    if not any(map(lambda x: x[0] == table, fetched)):
                        sql = getCreateTableSql(table).split(";")
                        for query in sql:
                            cursor.execute(query)
                            needCommit = True
            if needCommit:
                options.SQLConnection.commit()
    else:
        raise RuntimeError("No database connection")


def getCreateTableSql(name: str) -> str:
    if name == "web_pages":
        return """
        CREATE TABLE `web_pages` (
            `id` int(11) NOT NULL,
            `url` text NOT NULL,
            `content` longtext DEFAULT NULL,
            `status` varchar(20) NOT NULL,
            `author` int(11) NOT NULL,
            `name` text NOT NULL,
            `time_created` timestamp NOT NULL DEFAULT current_timestamp()
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
        INSERT INTO `web_pages` (`id`, `url`, `content`, `status`, `author`, `name`, `time_created`) VALUES
        (0, '$exception500', 'Internal server error. Sorry.', 'exception', 0, 'Internal server error', '2023-01-01 01:01:01');
        ALTER TABLE `web_pages`
            ADD PRIMARY KEY (`id`),
            ADD UNIQUE KEY `url` (`url`) USING HASH,
            ADD KEY `status` (`status`),
            ADD KEY `author` (`author`);
        ALTER TABLE `web_pages`
            MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
        ALTER TABLE `web_pages`
            ADD CONSTRAINT `web_pages_ibfk_1` FOREIGN KEY (`author`) REFERENCES `web_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
        """
    elif name == "web_users":
        return """
        CREATE TABLE `web_users` (
            `id` int(11) NOT NULL,
            `login` mediumtext NOT NULL,
            `pass_hash` mediumtext NOT NULL,
            `protection_level` int(11) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
        INSERT INTO `web_users` (`id`, `login`, `pass_hash`, `protection_level`) VALUES (0, 'WebS', '', 0);
        ALTER TABLE `web_users`
            ADD PRIMARY KEY (`id`) USING BTREE,
            ADD UNIQUE KEY `login` (`login`) USING HASH;
        ALTER TABLE `web_users`
            MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
        """
    elif name == "web_users_meta":
        return """
        CREATE TABLE `web_users_meta` (
            `id` int(11) NOT NULL,
            `user_id` int(11) NOT NULL,
            `meta_key` text NOT NULL,
            `meta_value` text NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
        ALTER TABLE `web_users_meta`
            ADD PRIMARY KEY (`id`),
            ADD KEY `user_id` (`user_id`);
        ALTER TABLE `web_users_meta`
            MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
        ALTER TABLE `web_users_meta`
            ADD CONSTRAINT `web_users_meta_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `web_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
        """
    elif name == "web_options":
        return """
        CREATE TABLE `web_options` (
            `id` int(11) NOT NULL,
            `option_key` varchar(20) NOT NULL,
            `option_value` text NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        ALTER TABLE `web_options`
            ADD PRIMARY KEY (`id`),
            ADD UNIQUE KEY `option_key` (`option_key`);
        ALTER TABLE `web_options`
            MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
        """
    return ""
