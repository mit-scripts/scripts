from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.protocols import basic
import ldap, ldap.filter
import posixpath

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
    def __init__(self, ldap_URL, ldap_base, keyFile):
        self.ldap_URL = ldap_URL
        self.ldap = ldap.initialize(self.ldap_URL)
        self.ldap_base = ldap_base
        self.key = file(keyFile).read()
    def canonicalize(self, vhost):
        vhost = vhost.lower().rstrip(".")
        return vhost
#        if vhost.endswith(".mit.edu"):
#            return vhost
#        else:
#            return vhost + ".mit.edu"
    def searchLDAP(self, vhost):
        attrlist = ('scriptsVhostName', 'homeDirectory', 'scriptsVhostDirectory', 'uid')
        results = self.ldap.search_st(self.ldap_base, ldap.SCOPE_SUBTREE,
            ldap.filter.filter_format(
                '(|(scriptsVhostName=%s)(scriptsVhostAlias=%s))', (vhost,)*2),
                attrlist=attrlist, timeout=5)
        if len(results) >= 1:
            result = results[0]
            attrs = result[1]
            for attr in attrlist:
                attrs[attr] = attrs[attr][0]
            return attrs
        else:
            return None
    def getWhois(self, vhost):
        vhost = self.canonicalize(vhost)
        info = None
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
                (info['scriptsVhostName'], vhost, info['uid'],
                 posixpath.join(info['homeDirectory'], 'web_scripts', info['scriptsVhostDirectory']))
        elif tries == 3:
            ret = "The whois server is experiencing problems looking up LDAP records.\nPlease contact scripts@mit.edu for help if this problem persists."
        else:
            ret = "No such hostname"
        return defer.succeed(ret)

application = service.Application('whois', uid=99, gid=99)
factory = WhoisFactory(
    "ldap://localhost", "ou=VirtualHosts,dc=scripts,dc=mit,dc=edu", "/etc/whoisd-password")
internet.TCPServer(43, factory).setServiceParent(
    service.IServiceCollection(application))
