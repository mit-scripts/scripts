#!/usr/bin/python

from subprocess import Popen, PIPE


# Make test.html in this directory available at this url:
URL = "http://cberzan.scripts.mit.edu/static-cat.cgi/test.html"


def test_all():
    truth =\
r"""HTTP/1.1 200 OK
Date: Sun, 12 Jun 2011 02:59:36 GMT
Server: Apache
Last-Modified: Sat, 11 Jun 2011 21:55:23 GMT
ETag: "823818c-2c6-4a576be3968c0"
Accept-Ranges: bytes
Content-Length: 710
Vary: Accept-Encoding
Content-Type: text/html

Sunt autem quidam e nostris, qui haec subtilius velint tradere et negent satis esse, quid bonum sit aut quid malum, sensu iudicari, sed animo etiam ac ratione intellegi posse et voluptatem ipsam per se esse expetendam et dolorem ipsum per se esse fugiendum. itaque aiunt hanc quasi naturalem atque insitam in animis nostris inesse notionem, ut alterum esse appetendum, alterum aspernandum sentiamus. Alii autem, quibus ego assentior, cum a philosophis compluribus permulta dicantur, cur nec voluptas in bonis sit numeranda nec in malis dolor, non existimant oportere nimium nos causae confidere, sed et argumentandum et accurate disserendum et rationibus conquisitis de voluptate et dolore disputandum putant."""
    p = Popen(["curl", URL, "-s", "-D", "-"], stdout=PIPE)
    result = p.communicate()[0]
    print "TODO finish test..."
    # LEFT TODO: use mimeheaders or something (http://stackoverflow.com/questions/4685217/parse-raw-http-headers)
    # to parse headers and make sure they're OK; compare content and make sure it matches byte-for-byte.


def test_one_range():
    truth =\
r"""HTTP/1.1 206 Partial Content
Date: Sun, 12 Jun 2011 03:05:41 GMT
Server: Apache
Last-Modified: Sat, 11 Jun 2011 21:55:23 GMT
ETag: "823818c-2c6-4a576be3968c0"
Accept-Ranges: bytes
Content-Length: 101
Vary: Accept-Encoding
Content-Range: bytes 100-200/710
Content-Type: text/html

aut quid malum, sensu iudicari, sed animo etiam ac ratione intellegi posse et voluptatem ipsam per se"""
    p = Popen(["curl", "-r", "100-200", URL, "-s", "-D", "-"], stdout=PIPE)
    result = p.communicate()[0]
    print "TODO finish test..."
    # LEFT TODO: see above


def test_overlapping_ranges():
    truth =\
r"""HTTP/1.1 206 Partial Content
Date: Sun, 12 Jun 2011 03:07:02 GMT
Server: Apache
Last-Modified: Sat, 11 Jun 2011 21:55:23 GMT
ETag: "823818c-2c6-4a576be3968c0"
Accept-Ranges: bytes
Content-Length: 395
Vary: Accept-Encoding
Content-Type: multipart/byteranges; boundary=4a57b18cf808c49ff


--4a57b18cf808c49ff
Content-type: text/html
Content-range: bytes 100-200/710

aut quid malum, sensu iudicari, sed animo etiam ac ratione intellegi posse et voluptatem ipsam per se
--4a57b18cf808c49ff
Content-type: text/html
Content-range: bytes 150-250/710

 ratione intellegi posse et voluptatem ipsam per se esse expetendam et dolorem ipsum per se esse fugi
 --4a57b18cf808c49ff--
"""
    p = Popen(["curl", "-r", "100-200,150-250", URL, "-s", "-D", "-"], stdout=PIPE)
    result = p.communicate()[0]
    print "TODO finish test..."
    # LEFT TODO: see above, with the additional complication that the separating string varies.


def test_nonoverlapping_ranges():
    truth =\
r"""HTTP/1.1 206 Partial Content
Date: Sun, 12 Jun 2011 03:08:19 GMT
Server: Apache
Last-Modified: Sat, 11 Jun 2011 21:55:23 GMT
ETag: "823818c-2c6-4a576be3968c0"
Accept-Ranges: bytes
Content-Length: 429
Vary: Accept-Encoding
Content-Type: multipart/byteranges; boundary=4a57b1d5f1d8949fd


--4a57b1d5f1d8949fd
Content-type: text/html
Content-range: bytes 50-100/710

lint tradere et negent satis esse, quid bonum sit a
--4a57b1d5f1d8949fd
Content-type: text/html
Content-range: bytes 150-200/710

 ratione intellegi posse et voluptatem ipsam per se
 --4a57b1d5f1d8949fd
 Content-type: text/html
 Content-range: bytes 250-300/710

 iendum. itaque aiunt hanc quasi naturalem atque ins
 --4a57b1d5f1d8949fd--
"""
    p = Popen(["curl", "-r", "50-100,150-200,250-300", URL, "-s", "-D", "-"], stdout=PIPE)
    result = p.communicate()[0]
    print "TODO finish test..."
    # LEFT TODO: see above, with the additional complication that the separating string varies.


if __name__ == "__main__":
    print "Unfinished tests! Read the source."
    test_all()
    test_one_range()
    test_overlapping_ranges()
    test_nonoverlapping_ranges()
    print "Test passed."
