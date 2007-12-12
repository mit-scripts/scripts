from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.protocols import basic
import os, sys, glob

class WhoisProtocol(basic.LineReceiver):
    def lineReceived(self, hostname):
        self.factory.getWhois(hostname
        ).addErrback(lambda _: "Internal error in server"
        ).addCallback(lambda m:
                      (self.transport.write(m+"\r\n"),
                       self.transport.loseConnection()))
class WhoisFactory(protocol.ServerFactory):
    protocol = WhoisProtocol
    def __init__(self, vhostDir):
        self.vhostDir = vhostDir
        self.vhosts = {}
        self.rescanVhosts()
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
                d = {'locker': locker, 'docroot': docroot, 'canonical': hostnames[0]}
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
    def getWhois(self, vhost):
        vhost = self.canonicalize(vhost)
        info = self.vhosts.get(vhost)
        if info:
            ret = "Hostname: %s\nAlias: %s\nLocker: %s\nDocument Root: %s" % \
                (info['canonical'], vhost, info['locker'], info['docroot'])
        else:
            ret = "No such hostname"
        return defer.succeed(ret)

application = service.Application('whois', uid=99, gid=99)
factory = WhoisFactory("/etc/httpd/vhosts.d")
internet.TCPServer(43, factory).setServiceParent(
    service.IServiceCollection(application))
