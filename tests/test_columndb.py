import unittest
import pynosql.columndb
from pynosql import (ConnectError, DatabaseCreationError, DatabaseDeletionError, DatabaseError)
from unittest import mock


class MyDBConnection(pynosql.columndb.ColumnConnection):
    # Simulate socket.socket
    t = mock.Mock('AF_INET', 'SOCK_STREAM')
    t.connect = mock.MagicMock()
    t.send = mock.MagicMock()
    t.close = mock.MagicMock()

    def __bool__(self):
        if self.return_data:
            return True

    def close(self):
        self.connection.close()
        self.connection = None
        self.t.recv = mock.MagicMock(return_value='CLOSED')
        self._return_data = self.t.recv(2048)
        if self.return_data != 'CLOSED':
            raise ConnectError(f'Close connection error: {self.return_data}')

    def connect(self):
        # Connection
        self.t.connect(self.host, self.port)
        if self.database:
            self.t.send(f"CLIENT_CONNECT_WITH_DB={self.database}")
        else:
            self.t.send("CLIENT_CONNECT")
        # Check credential
        if self.username and self.password:
            self.t.send(f"\nCRED={self.username}:{self.password}")
        # while len(self.t.recv(2048)) > 0:
        self.t.recv = mock.MagicMock(return_value='OK_PACKET')
        self._return_data = self.t.recv(2048)
        if self.return_data != 'OK_PACKET':
            raise ConnectError(f'Server connection error: {self.return_data}')
        self.connection = self.t
        # return MyDBSession(self.connection)

    def create_database(self, name):
        if self.connection:
            self.connection.send(f"CREATE_DB='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_CREATED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_CREATED':
                raise DatabaseCreationError(f'Database creation error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def has_database(self, name):
        if self.connection:
            self.connection.send(f"DB_EXISTS='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_EXISTS')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_EXISTS':
                return False
            else:
                return True
        else:
            raise ConnectError(f"Server isn't connected")

    def delete_database(self, name):
        if self.connection:
            self.connection.send(f"DELETE_DB='{name}'")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='DB_DELETED')
            self._return_data = self.t.recv(2048)
            if self.return_data != 'DB_DELETED':
                raise DatabaseDeletionError(f'Database deletion error: {self.return_data}')
        else:
            raise ConnectError(f"Server isn't connected")

    def databases(self):
        if self.connection:
            self.connection.send(f"GET_ALL_DBS")
            # while len(self.t.recv(2048)) > 0:
            self.t.recv = mock.MagicMock(return_value='test_db db1 db2')
            self._return_data = self.t.recv(2048)
            if not self:
                raise DatabaseError(f'Request error: {self.return_data}')
            # return MyDBResponse(self.return_data.split())
        else:
            raise ConnectError(f"Server isn't connected")


class ColumnConnectionTest(unittest.TestCase):
    def test_kvdb_connect(self):
        myconn = MyDBConnection('mycolumndb.local', 12345, username='admin', password='pass')
        myconn.connect()
        self.assertEqual(myconn.return_data, 'OK_PACKET')


if __name__ == '__main__':
    unittest.main()
