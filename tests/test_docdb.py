import unittest
import nosqlapi.docdb
import json
from unittest import mock
from nosqlapi import (ConnectError, DatabaseCreationError, DatabaseDeletionError, DatabaseError, SessionError,
                      SessionInsertingError, SelectorAttributeError, SessionUpdatingError, SessionDeletingError,
                      SessionFindingError, SessionACLError)


# Below classes is a simple emulation of MongoDB like database


class MyDBConnection(nosqlapi.docdb.DocConnection):
    # Simulate http requests
    req = mock.Mock()

    def close(self):
        self.connection = None
        if self.connection is not None:
            raise ConnectError('Close connection error')

    def connect(self):
        # Connection
        scheme = 'https://' if self.ssl else 'http://'
        if self.username and self.password:
            scheme += f'{self.username}:{self.password}@'
        url = f'{scheme}{self.host}'
        self.req.get = mock.MagicMock(return_value={'body': 'server http response ok',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self.req.get(url).get('status') != 200:
            raise ConnectError('server not respond')
        self.connection = url
        return MyDBSession(self.connection)

    def create_database(self, name):
        self.req.put = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self.connection:
            ret = self.req.put(f"{self.connection}/{name}")
            if ret.get('status') != 200:
                raise DatabaseCreationError(f'Database creation error: {ret.get("status")}')
            return MyDBResponse(json.loads(ret['body']),
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")

    def has_database(self, name):
        if self.connection:
            if name in self.databases():
                return True
            else:
                return False
        else:
            raise ConnectError("server isn't connected")

    def delete_database(self, name):
        self.req.delete = mock.MagicMock(return_value={'body': '{"result": "ok"}',
                                                       'status': 200,
                                                       'header': '"Content-Type": [ "application/json" ]'})
        if self.connection:
            ret = self.req.delete(f"{self.connection}/{name}")
            if ret.get('status') != 200:
                raise DatabaseDeletionError(f'Database deletion error: {ret.get("status")}')
            return MyDBResponse(json.loads(ret['body']),
                                ret['status'],
                                ret['header'])
        else:
            raise ConnectError("server isn't connected")

    def databases(self):
        self.req.get = mock.MagicMock(return_value={'body': '{"result": ["test_db", "db1", "db2"]}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        if self.connection:
            ret = self.req.get(f"{self.connection}/databases")
            dbs = json.loads(ret.get('body'))
            if dbs['result']:
                return MyDBResponse(dbs['result'],
                                    ret['status'],
                                    ret['header'])
            else:
                raise DatabaseError('no databases found on this server')
        else:
            raise ConnectError("server isn't connected")


class MyDBSession(nosqlapi.docdb.DocSession):
    # Simulate http requests
    req = mock.Mock()

    def __init__(self, connection):
        super().__init__()
        self.session = connection
        self.req.get = mock.MagicMock(return_value={'body': '{"host" : "mydocdb.local",\n"version" : "1.0",\n'
                                                            '"uptime" : 123445566}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.session}/serverStatus")
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        self._description = json.loads(ret.get('body'))

    @property
    def acl(self):
        self.req.get = mock.MagicMock(return_value={'body': '{"user": "admin", "roles": ["administrator", "all"]}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.session}/privileges")
        if ret.get('status') != 200:
            raise ConnectError('server not respond')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def get(self, path):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.get = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                            '"name": "Matteo", "age": 35}',
                                                    'status': 200,
                                                    'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.get(f"{self.session}/{path}")
        if ret.get('status') != 200:
            raise SessionError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert(self, path, doc):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"revision": 1}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.session}/{path}", doc)
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def insert_many(self, path, *docs):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"insertedIds": [ "5099803df3f4948bd2f98391", '
                                                             '"5099803df3f4948bd2f98392", '
                                                             '"5099803df3f4948bd2f98393"]}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        ret = self.req.post(f"{self.session}/{path}", f"{[doc for doc in docs]}")
        if ret.get('status') != 200:
            raise SessionInsertingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update(self, path, doc, rev):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"revision": 2}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        doc_with_rev = json.loads(doc)
        doc_with_rev['revision'] = 2
        ret = self.req.post(f"{self.session}/{path}", json.dumps(doc_with_rev))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def update_many(self, path, query, *docs):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"insertedIds": [ "5099803df3f4948bd2f98391", '
                                                             '"5099803df3f4948bd2f98392", '
                                                             '"5099803df3f4948bd2f98393"]}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        doc_with_rev = {"docs": f"{list(docs)}", 'query': query}
        ret = self.req.post(f"{self.session}/{path}", json.dumps(doc_with_rev))
        if ret.get('status') != 200:
            raise SessionUpdatingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def delete(self, path, rev=None):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.delete = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                               '"revision": 3}',
                                                       'status': 200,
                                                       'header': '"Content-Type": [ "application/json" ]'})
        if not rev:
            ret = self.req.delete(f"{self.session}/{path}")
        else:
            ret = self.req.delete(f"{self.session}/{path}?revision={rev}")
        if ret.get('status') != 200:
            raise SessionDeletingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def close(self):
        self.session = None

    def find(self, selector):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': '{"_id": "5099803df3f4948bd2f98391",'
                                                             '"name": "Matteo", "age": 35}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        if isinstance(selector, nosqlapi.docdb.DocSelector):
            ret = self.req.post(f"{self.session}/find", selector.build())
        else:
            ret = self.req.post(f"{self.session}/find", selector)
        if ret.get('status') != 200:
            raise SessionFindingError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def grant(self, database, user, role):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': f'{{"user": "{user}",'
                                                             f'"role": "{role}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        role_ = dict()
        role_[user] = {"role": role, "db": database}
        ret = self.req.post(f"{self.session}/grantRolesToUser", json.dumps(role_))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])

    def revoke(self, database, role):
        if not self.session:
            raise ConnectError('connect to a server before some request')
        self.req.post = mock.MagicMock(return_value={'body': f'{{"role": "{role}"}}',
                                                     'status': 200,
                                                     'header': '"Content-Type": [ "application/json" ]'})
        role_ = {"role": role, "db": database}
        ret = self.req.post(f"{self.session}/revokeRolesFromUser", json.dumps(role_))
        if ret.get('status') != 200:
            raise SessionACLError(f'error: {ret.get("body")}, status: {ret.get("status")}')
        return MyDBResponse(json.loads(ret.get('body')),
                            ret['status'],
                            ret['header'])


class MyDBResponse(nosqlapi.docdb.DocResponse):
    pass


class MyDBSelector(nosqlapi.docdb.DocSelector):

    def build(self):
        query = dict()
        if not self.selector:
            raise SelectorAttributeError("selector is mandatory")
        query["selector"] = self.selector
        if self.fields:
            query["fields"] = self.fields
        if self.limit:
            query["limit"] = self.limit
        if self.partition:
            query["partition"] = self.partition
        if self.condition:
            query["condition"] = self.condition
        if self.order:
            query["order"] = self.order
        return json.dumps(query)


class DocConnectionTest(unittest.TestCase):
    def test_kvdb_connect(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local')

    def test_kvdb_close(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local')
        myconn.close()
        self.assertEqual(myconn.connection, None)

    def test_kvdb_create_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local')
        resp = myconn.create_database('test_db')
        self.assertEqual(resp.data['result'], 'ok')
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_kvdb_exists_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local')
        self.assertTrue(myconn.has_database('test_db'))
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_kvdb_delete_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local')
        resp = myconn.delete_database('test_db')
        self.assertEqual(resp.data['result'], 'ok')
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')

    def test_kvdb_get_all_database(self):
        myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
        myconn.connect()
        self.assertEqual(myconn.connection, 'http://admin:test@mydocdb.local')
        dbs = myconn.databases()
        self.assertIsInstance(dbs, MyDBResponse)
        self.assertEqual(dbs.data, ['test_db', 'db1', 'db2'])
        myconn.close()
        self.assertEqual(myconn.connection, None)
        self.assertRaises(ConnectError, myconn.create_database, 'test_db')


class DocSessionTest(unittest.TestCase):
    myconn = MyDBConnection('mydocdb.local', 12345, username='admin', password='test')
    mysess = myconn.connect()

    def test_session_instance(self):
        self.assertIsInstance(self.mysess, MyDBSession)

    def test_description_session(self):
        self.assertEqual(self.mysess.description, {'host': 'mydocdb.local', 'version': '1.0', 'uptime': 123445566})

    def test_get_data(self):
        d = self.mysess.get('db/doc1')
        self.assertIsInstance(d, MyDBResponse)
        self.assertIn('_id', d)
        self.assertEqual(d.data['_id'], '5099803df3f4948bd2f98391')

    def test_insert_data(self):
        ret = self.mysess.insert('db/doc1', '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}')
        self.assertEqual(ret.data['revision'], 1)

    def test_insert_many_data(self):
        ret = self.mysess.insert_many('db',
                                      '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}',
                                      '{"_id": "5099803df3f4948bd2f98392", "name": "Matteo", "age": 35}',
                                      '{"_id": "5099803df3f4948bd2f98393", "name": "Matteo", "age": 35}')
        self.assertEqual(ret.data['insertedIds'], ["5099803df3f4948bd2f98391",
                                                   "5099803df3f4948bd2f98392",
                                                   "5099803df3f4948bd2f98393"])

    def test_update_data(self):
        ret = self.mysess.update('db/doc1', '{"_id": "5099803df3f4948bd2f98391", "name": "Matteo", "age": 35}', rev=1)
        self.assertEqual(ret.data['revision'], 2)


if __name__ == '__main__':
    unittest.main()
