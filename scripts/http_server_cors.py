#!/usr/bin/env python3
"""Use instead of `python3 -m http.server 8000` when you need CORS"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        return super(CORSRequestHandler, self).end_headers()


class QuietHTTPServer(HTTPServer):
    """Suppress BrokenPipeError tracebacks from disconnected clients."""

    def handle_error(self, request, client_address):

        exc = sys.exc_info()[1]
        if isinstance(exc, BrokenPipeError):
            return  # Client disconnected — safe to ignore
        super().handle_error(request, client_address)


httpd = QuietHTTPServer(("localhost", 8000), CORSRequestHandler)
httpd.serve_forever()
