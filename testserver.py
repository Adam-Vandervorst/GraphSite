from sys import argv
from urllib.parse import urlsplit, urlunsplit
import http.server


class PythonServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        (s, n, p, q, f) = urlsplit(self.path)
        if p == "/": p += ENTRY
        if "." not in p: p += ".html"
        self.path = urlunsplit((s, n, PATH + p, q, f))
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


PORT = int(argv[1]) if len(argv) >= 2 else 4002
ENTRY = argv[2] if len(argv) >= 3 else "index"
PATH = argv[3] if len(argv) >= 4 else __file__[:-len(argv[0])]
webServer = http.server.HTTPServer(("localhost", PORT), PythonServer)
print(f"Serving files in {PATH} at http://localhost:{PORT}")

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    webServer.server_close()
