#!/usr/bin/env python3
"""Use instead of `python3 -m http.server 8000` when you need CORS"""

from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(CORSRequestHandler, self).end_headers()

httpd = HTTPServer(('localhost', 8000), CORSRequestHandler)
httpd.serve_forever()
