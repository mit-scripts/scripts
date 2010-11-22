from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.protocols import basic
import ldap, ldap.filter
import os, sys, pwd, glob

class WhoisProtocol(basic.LineReceiver):
    def lineReceived(self, hostname):
    	(key, hostname) = hostname.split('=',2)
	if key != self.factory.key:
            self.transport.write("Unauthorized to use whois"+"\r\n")
	    self.transport.loseConnection()
	else:
            self.factory.getWhois(hostname
            ).addErrback(lambda _: "Internal error in server"
            ).addCallback(lambda m:
                          (self.transport.write(m+"\r\n"),
                           self.transport.loseConnection()))
class WhoisFactory(protocol.ServerFactory):
    protocol = WhoisProtocol
    def __init__(self, vhostDir, ldap_URL, ldap_base, keyFile):
        self.vhostDir = vhostDir
        self.ldap_URL = ldap_URL
        self.ldap = ldap.initialize(self.ldap_URL)
        self.ldap_base = ldap_base
        self.vhosts = {}
        if vhostDir:
            self.rescanVhosts()
        self.key = file(keyFile).read()
    def rescanVhosts(self):
        newVhosts = {}
        for f in glob.iglob(os.path.join(self.vhostDir, "*.conf")):
            locker = os.path.splitext(os.path.basename(f))[0]
            newVhosts.update(self.parseApacheConf(file(f)))
        self.vhosts = newVhosts
        self.vhostTime = os.stat(self.vhostDir).st_mtime
    def parseApacheConf(self, f):
        vhosts = {}
        hostnames = []
        locker = None
        docroot = None
        for l in f:
            parts = l.split()
            if not parts: continue
            command = parts.pop(0)
            if command in ("ServerName", "ServerAlias"):
                hostnames.extend(parts)
            elif command in ("SuExecUserGroup",):
                locker = parts[0]
            elif command in ("DocumentRoot",):
                docroot = parts[0]
            elif command == "</VirtualHost>":
                d = {'locker': locker, 'apacheDocumentRoot': docroot, 'apacheServerName': hostnames[0]}
                for h in hostnames: vhosts[h] = d
                hostnames = []
                locker = None
                docroot = None
        return vhosts
    def canonicalize(self, vhost):
        vhost = vhost.lower().rstrip(".")
        return vhost
#        if vhost.endswith(".mit.edu"):
#            return vhost
#        else:
#            return vhost + ".mit.edu"
    def searchLDAP(self, vhost):
        results = self.ldap.search_st(self.ldap_base, ldap.SCOPE_SUBTREE,
            ldap.filter.filter_format(
                '(|(apacheServername=%s)(apacheServerAlias=%s))', (vhost,)*2),
                timeout=5)
        if len(results) >= 1:
            result = results[0]
            attrs = result[1]
            for attr in ('apacheServerName','apacheDocumentRoot', 'apacheSuexecUid', 'apacheSuexecGid'):
                attrs[attr] = attrs[attr][0]
            user = pwd.getpwuid(int(attrs['apacheSuexecUid']))
            if user:
                attrs['locker'] = user.pw_name
            else:
                attrs['locker'] = None
            return attrs
        else:
            return None
    def getWhois(self, vhost):
        vhost = self.canonicalize(vhost)
        info = self.vhosts.get(vhost)
        tries = 0
        while (tries < 3) and not info:
            tries += 1
            try:
                info = self.searchLDAP(vhost)
                break
            except (ldap.TIMEOUT, ldap.SERVER_DOWN):
                self.ldap.unbind()
                self.ldap = ldap.initialize(self.ldap_URL)
        if info:
            ret = "Hostname: %s\nAlias: %s\nLocker: %s\nDocument Root: %s" % \
                (info['apacheServerName'], vhost, info['locker'], info['apacheDocumentRoot'])
        elif tries == 3:
            ret = "The whois server is experiencing problems looking up LDAP records.\nPlease contact scripts@mit.edu for help if this problem persists."
        else:
            ret = "No such hostname"
        return defer.succeed(ret)

application = service.Application('whois', uid=99, gid=99)
factory = WhoisFactory(None,
    "ldap://localhost", "ou=VirtualHosts,dc=scripts,dc=mit,dc=edu", "/etc/whoisd-password")
internet.TCPServer(43, factory).setServiceParent(
    service.IServiceCollection(application))
