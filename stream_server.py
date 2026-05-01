import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer

frame_global = None


def set_frame(frame):
    """Expose the latest processed frame to the MJPEG streaming handler."""
    global frame_global
    frame_global = frame


class StreamHandler(BaseHTTPRequestHandler):
    """Simple MJPEG endpoint that continuously serves the latest frame."""

    def do_GET(self):
        """Serve `/stream` as a multipart JPEG response."""

        if self.path != "/stream":
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
        self.end_headers()

        while True:

            if frame_global is None:
                continue

            _, jpeg = cv2.imencode('.jpg', frame_global)

            self.wfile.write(b'--frame\r\n')
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', str(len(jpeg)))
            self.end_headers()
            self.wfile.write(jpeg.tobytes())
            self.wfile.write(b'\r\n')


def start_stream_server(port=8888):
    """Start the MJPEG HTTP server in a background thread."""

    server = HTTPServer(('0.0.0.0', port), StreamHandler)

    import threading
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print(f"Stream server running on port {port}")
