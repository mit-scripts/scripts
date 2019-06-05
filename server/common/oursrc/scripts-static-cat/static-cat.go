package main

import (
	"log"
	"net/http"
	"net/http/cgi"
	"os"
	"path"
	"strings"
)

var mimeTypes = map[string]string{
	".avi":   "video/x-msvideo",
	".css":   "text/css",
	".doc":   "application/msword",
	".docm":  "application/vnd.ms-word.document.macroEnabled.12",
	".docx":  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	".dot":   "application/msword",
	".dotm":  "application/vnd.ms-word.template.macroEnabled.12",
	".dotx":  "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
	".eot":   "application/vnd.ms-fontobject",
	".gif":   "image/gif",
	".htm":   "text/html",
	".html":  "text/html",
	".ico":   "image/vnd.microsoft.icon",
	".il":    "application/octet-stream",
	".jar":   "application/java-archive",
	".jpeg":  "image/jpeg",
	".jpg":   "image/jpeg",
	".js":    "application/javascript",
	".mid":   "audio/midi",
	".midi":  "audio/midi",
	".mov":   "video/quicktime",
	".mp3":   "audio/mpeg",
	".mpeg":  "video/mpeg",
	".mpg":   "video/mpeg",
	".odb":   "application/vnd.oasis.opendocument.database",
	".odc":   "application/vnd.oasis.opendocument.chart",
	".odf":   "application/vnd.oasis.opendocument.formula",
	".odg":   "application/vnd.oasis.opendocument.graphics",
	".odi":   "application/vnd.oasis.opendocument.image",
	".odm":   "application/vnd.oasis.opendocument.text-master",
	".odp":   "application/vnd.oasis.opendocument.presentation",
	".ods":   "application/vnd.oasis.opendocument.spreadsheet",
	".odt":   "application/vnd.oasis.opendocument.text",
	".otf":   "application/font-sfnt",
	".otg":   "application/vnd.oasis.opendocument.graphics-template",
	".oth":   "application/vnd.oasis.opendocument.text-web",
	".otp":   "application/vnd.oasis.opendocument.presentation-template",
	".ots":   "application/vnd.oasis.opendocument.spreadsheet-template",
	".ott":   "application/vnd.oasis.opendocument.text-template",
	".pdf":   "application/pdf",
	".png":   "image/png",
	".pot":   "application/vnd.ms-powerpoint",
	".potm":  "application/vnd.ms-powerpoint.template.macroEnabled.12",
	".potx":  "application/vnd.openxmlformats-officedocument.presentationml.template",
	".ppa":   "application/vnd.ms-powerpoint",
	".ppam":  "application/vnd.ms-powerpoint.addin.macroEnabled.12",
	".pps":   "application/vnd.ms-powerpoint",
	".ppsm":  "application/vnd.ms-powerpoint.slideshow.macroEnabled.12",
	".ppsx":  "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
	".ppt":   "application/vnd.ms-powerpoint",
	".pptm":  "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
	".pptx":  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
	".ps":    "application/postscript",
	".svg":   "image/svg+xml",
	".swf":   "application/x-shockwave-flash",
	".tar":   "application/x-tar",
	".tgz":   "application/gzip",
	".tif":   "image/tiff",
	".tiff":  "image/tiff",
	".ttf":   "application/font-sfnt",
	".wav":   "audio/x-wav",
	".wmv":   "video/x-ms-wmv",
	".woff":  "application/font-woff",
	".woff2": "font/woff2",
	".xaml":  "application/xaml+xml",
	".xap":   "application/x-silverlight-app",
	".xhtml": "application/xhtml+xml",
	".xla":   "application/vnd.ms-excel",
	".xlam":  "application/vnd.ms-excel.addin.macroEnabled.12",
	".xls":   "application/vnd.ms-excel",
	".xlsb":  "application/vnd.ms-excel.sheet.binary.macroEnabled.12",
	".xlsm":  "application/vnd.ms-excel.sheet.macroEnabled.12",
	".xlsx":  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	".xlt":   "application/vnd.ms-excel",
	".xltm":  "application/vnd.ms-excel.template.macroEnabled.12",
	".xltx":  "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
	".xml":   "text/xml",
	".xsl":   "application/xslt+xml",
	".zip":   "application/zip",
}

func writeError(w http.ResponseWriter, err error) {
	if os.IsNotExist(err) {
		http.Error(w, "404 Not Found", http.StatusNotFound)
		return
	}
	if os.IsPermission(err) {
		http.Error(w, "403 Forbidden", http.StatusForbidden)
		return
	}
	http.Error(w, "500 Internal Server Error", http.StatusInternalServerError)
}

func handle(w http.ResponseWriter, r *http.Request) {
	p := os.Getenv("PATH_TRANSLATED")
	ext := path.Ext(p)
	mime := mimeTypes[strings.ToLower(ext)]
	if mime == "" {
		http.Error(w, "403 Forbidden Extension", http.StatusForbidden)
		return
	}
	// Explicitly set the content-type; otherwise ServeContent
	// will attempt to infer from the file's magic.
	w.Header().Set("Content-Type", mime)
	// Open and stat the file.
	f, err := os.Open(p)
	if err != nil {
		writeError(w, err)
		return
	}
	defer f.Close()
	d, err := f.Stat()
	if err != nil {
		writeError(w, err)
		return
	}
	// Check to make sure it's a regular file we're trying to serve.
	if !d.Mode().IsRegular() {
		http.Error(w, "403 Forbidden Mode", http.StatusForbidden)
		return
	}
	// Standard library handles range, if-modified-since, etc.
	http.ServeContent(w, r, "", d.ModTime(), f)
}

func main() {
	if err := cgi.Serve(http.HandlerFunc(handle)); err != nil {
		log.Fatal(err)
	}
}
