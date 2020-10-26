import pkg_resources
import threading
import varlink

# Monkey-patch varlink.scanner
# systemd uses uppercase service names, which python-varlink rejects.
import varlink.scanner
orig_init = varlink.scanner.Scanner.__init__
def scanner_init(self, string):
    orig_init(self, string)
    self.patterns['interface-name'] = re.compile(r'[a-z]([-]*[a-z0-9])*([.][a-zA-Z0-9]([-]*[a-zA-Z0-9])*)+')
varlink.scanner.Scanner.__init__ = scanner_init

varlink_service = varlink.Service(
    vendor='SIPB',
    product='JupyterHub',
    version='1',
    url='http://jupyter.mit.edu',
    interface_dir=pkg_resources.resource_filename(__name__, 'interface'),
)

class ServiceRequestHandler(varlink.RequestHandler):
    service = varlink_service

class UserDBError(varlink.VarlinkError):
    def __init__(self):
        super().__init__(
            self,
            {
                'error': 'io.systemd.UserDatabase.' + self.__class__.__name__,
                'parameters': {},
            })
class NoRecordFound(UserDBError): pass
class BadService(UserDBError): pass
class ServiceNotAvailable(UserDBError): pass
class ConflictingRecordFound(UserDBError): pass
class EnumerationNotSupported(UserDBError): pass

@varlink_service.interface('io.systemd.UserDatabase')
class UserDatabase(object):
    def GetUserRecord(self, uid=None, userName=None, service=None, _more=True, _server=None):
        # If uid and userName are both specified, return ConflictingRecordFound if they don't match.
        # If one is specified, return the record
        # If zero are specified, return all users
        if userName or uid:
            with _server.lock:
                user = _server.users_by_uid.get(uid)
                if not user:
                    user = _server.users_by_userName(userName)
            if not user:
                raise NoRecordFound()
            if userName and user['userName'] != userName:
                raise ConflictingRecordError()
            if uid and user['uid'] != uid:
                raise ConflictingRecordError()
            yield {
                'record': user,
                'incomplete': False,
            }
            return
        if not _more:
            raise InvalidParameter('more')
        with _server.lock:
            returns = [{
                'record': user,
                'incomplete': False,
                '_continues': True,
            } for user in _server.users_by_uid.values()]
        returns[-1]['_continues'] = False
        for r in returns:
            yield r
        if not returns:
            raise NoRecordFound()

    def GetGroupRecord(self, gid=None, groupName=None, service=None, _more=True, _server=None):
        # yield {
        #     'record': {},
        #     'incomplete': False,
        #     '_continues': True,
        # }
        raise NoRecordFound()
    def GetMemberships(self, userName=None, groupName=None, service=None, _more=True, _server=None):
        # yield {
        #     'userName': '',
        #     'groupName': '',
        #     '_continues': False,
        # }
        raise NoRecordFound()

class UserDatabaseServer(varlink.ThreadingServer):
    lock = threading.Lock()
    users_by_uid = {}
    users_by_name = {}

    def add_user(self, uid, userName, homeDirectory):
        # Consider setting: umask, environment
        user = {
            'uid': uid,
            'gid': 101,
            'userName': userName,
            'realm': 'edu.mit.jupyter',
            'disposition': 'regular',
            'shell': '/bin/bash',
            'homeDirectory': homeDirectory,
        }
        with self.lock:
            users_by_uid[uid] = user
            users_by_name[userName] = user

def run_server(address):
    with UserDatabaseServer('unix:/run/systemd/userdb/edu.mit.jupyter.User', ServiceRequestHandler) as server:
        print("Listening on", server.server_address)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
