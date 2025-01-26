from io import StringIO
from flask import redirect , send_file
from dash import Dash
import sys
from .utils import process_log , make_static

def dash2html(app:Dash,port:int=8080):
    print(f"first visit the http://127.0.0.1:{port} \nthen visit http://127.0.0.1:{port}/download_zip to download the static site")
    log_file = StringIO()
    sys.stderr = log_file
    @app.server.get("/download_zip")
    def api():
        log = log_file.getvalue()
        json_paths, extra_res = process_log(log)
        if not(json_paths and extra_res):
            return redirect("/")
        return send_file(make_static(f'http://127.0.0.1:{port}/',json_paths,extra_res), as_attachment=True, download_name='static_site.zip')
    app.run_server(debug=False,port=port)
    sys.stderr = sys.__stderr__