try:
    from flask import Flask, Response, render_template
    from flask_cors import CORS
    from werkzeug.serving import make_server
except ImportError:
    raise ImportError(
        "The 'live_viewer' submodule requires more dependencies than the base photonforge module. "
        "Please install all dependencies by, e.g., 'pip install photonforge[live_viewer]'."
    )

import threading
import queue
import logging
import time


class LiveViewer:
    """Live viewer for PhotonForge objects.

    Args:
        port: Port number used by the viewer server.
        start: If ``True``, the viewer server is automatically started.

    Example:
        >>> from photonforge.live_viewer import LiveViewer
        >>> viewer = LiveViewer()

        >>> component = pf.parametric.straight(port_spec="Strip", length=3)
        >>> viewer.display(component)

        >>> terminal = pf.Terminal("METAL", pf.Circle(2))
        >>> viewer.display(terminal)
    """

    def __init__(self, port=5001, start=True):
        self.app = Flask(__name__)
        CORS(self.app)
        self.port = port
        self.queue = queue.Queue()
        self.current_data = ""
        self.server = None
        self.is_running = False

        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        @self.app.route("/")
        def home():
            return render_template("index.html")

        @self.app.route("/events")
        def events():
            def generate():
                while self.is_running:
                    try:
                        while not self.queue.empty():
                            self.current_data = self.queue.get_nowait()
                    except queue.Empty:
                        pass
                    if self.current_data:
                        yield f"data: {self.current_data}\n\n"
                    else:
                        yield "data: Waiting for data…\n\n"
                    time.sleep(0.25)

            return Response(generate(), mimetype="text/event-stream")

        if start:
            print(f"Starting live viewer at http://localhost:{self.port}")
            self.start()

    def _run_server(self):
        self.server = make_server("0.0.0.0", self.port, self.app)
        self.is_running = True
        self.server.serve_forever()

    def start(self):
        """Start the server."""
        # Don't mark this thread as daemon, so it keeps the process alive.
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = False
        self.server_thread.start()
        return self

    def stop(self):
        """Stop the server."""
        if self.server:
            print("Stopping live viewer server…")
            self.is_running = False
            self.server.shutdown()
            print("Server stopped successfully")

    def display(self, item):
        """Display an item with an SVG representation."""
        if hasattr(item, "_repr_svg_"):
            self.queue.put(item._repr_svg_())
        return self

    def _repr_html_(self):
        """Returns a clickable link for Jupyter."""
        return (
            f'Live viewer at <a href="http://localhost:{self.port}" target="_blank">'
            f"http://localhost:{self.port}</a>"
        )
