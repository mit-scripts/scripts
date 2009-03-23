-- lighty.header["X-Maintenance-Mode"] = "1" 
-- uncomment the above if you want to add the header
lighty.content = { { filename = "/etc/lighttpd/scripts-maint/index.html" } }
lighty.header["Content-Type"] = "text/html"
return 503
-- or return 200 if you want