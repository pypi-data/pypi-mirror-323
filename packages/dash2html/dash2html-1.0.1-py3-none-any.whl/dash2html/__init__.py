from io import StringIO
from flask import send_file , redirect
from shutil import make_archive
from tempfile import TemporaryDirectory
from dash import Dash
from pathlib import Path
import sys
from utils import process_log , make_static
def dash2html(app:Dash,port:int=8080):
    print(f"first visit the http://127.0.0.1:{port} then visit http://127.0.0.1:{port}/download_zip to download the static site")
    log_file = StringIO()
    sys.stderr = log_file
    used = False
    @app.server.get("/download_zip")
    def api():
        nonlocal used
        if used:
            return send_file("static_site.zip", as_attachment=True)
        log_lines = log_file.getvalue().splitlines()
        log_file.seek(0)
        json_paths, js_script = process_log(log_lines)
        if not(json_paths and js_script):
            return redirect("/")
        with TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)
            make_static(f'http://127.0.0.1:{port}/',list(json_paths),list(js_script),tempdir)
            make_archive("static_site", 'zip', tempdir)
            sys.stderr = sys.__stderr__
            used = True
            return send_file("static_site.zip", as_attachment=True)
    app.run_server(debug=False,port=port)
    Path("static_site.zip").unlink(True)