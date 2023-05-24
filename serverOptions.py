from mysql.connector import MySQLConnection
from mysql.connector.pooling import PooledMySQLConnection

ServerName: str = "Python HTTP Web Server"
ServerHost: str = "localhost"
ServerPort: int = 8000
SSLCertificate: str = ""
SSLKey: str = ""

SQLPort: int = 3306
SQLHost: str = "localhost"
SQLUser: str = "root"
SQLPassword: str = ""
SQLDBName: str = "test"
SQLConnection: PooledMySQLConnection | MySQLConnection | None = None