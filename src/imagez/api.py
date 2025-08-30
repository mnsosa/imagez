from flask import Flask, request, send_from_directory, render_template_string, url_for, abort, make_response
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from pathlib import Path
import uuid
from imagez.main import parse_rgb, process_image

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR.mkdir(exist_ok=True, parents=True)
OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)

def get_html_template() -> str:
    from imagez.template import HTML_TEMPLATE
    return HTML_TEMPLATE

@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

@app.route("/", methods=["GET", "POST"])
def index():
    downloads = None
    if request.method == "POST":
        f = request.files.get("path")
        if f and f.filename:
            safe_name = secure_filename(f.filename)
            if not safe_name:
                abort(400, "Invalid filename")
            input_path = UPLOADS_DIR / f"{uuid.uuid4()}_{safe_name}"
            f.save(str(input_path))

            width_cm = float(request.form.get("width_cm", 20.0))
            height_cm = float(request.form.get("height_cm", 25.0))
            padding = request.form.get("padding_text", request.form.get("padding", "#000000"))
            dpi = int(request.form.get("dpi", 300))
            mode = request.form.get("mode", "todo").lower()

            try:
                rgb = parse_rgb(padding)
            except ValueError:
                input_path.unlink(missing_ok=True)
                abort(400, "Invalid padding color format. Use '#RRGGBB' or 'R,G,B'.")

            job_id = uuid.uuid4().hex
            job_out_dir = OUTPUTS_DIR / job_id
            job_out_dir.mkdir(parents=True, exist_ok=True)

            target_png, a4_png, pdf_path = process_image(
                str(input_path), str(job_out_dir), width_cm, height_cm, rgb, dpi, mode
            )

            downloads = []
            if target_png:
                downloads.append(("Download Target PNG",
                                  url_for("download", subpath=f"{job_id}/{Path(target_png).name}")))
            if a4_png:
                downloads.append(("Download A4 PNG",
                                  url_for("download", subpath=f"{job_id}/{Path(a4_png).name}")))
            if pdf_path:
                downloads.append(("Download PDF",
                                  url_for("download", subpath=f"{job_id}/{Path(pdf_path).name}")))

            input_path.unlink(missing_ok=True)

    return render_template_string(get_html_template(), downloads=downloads)

@app.route("/outputs/<path:subpath>")
def download(subpath: str):
    safe_path = safe_join(str(OUTPUTS_DIR), subpath)
    if not safe_path:
        abort(404)
    file_path = Path(safe_path)
    if not file_path.exists() or not file_path.is_file():
        abort(404)

    resp = make_response(send_from_directory(
        directory=str(OUTPUTS_DIR),
        path=subpath,
        as_attachment=True,
        download_name=file_path.name,
        max_age=0
    ))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    # clean
    job_dir = file_path.parent
    try:
        for f in job_dir.iterdir():
            f.unlink()
        job_dir.rmdir()
    except Exception as e:
        app.logger.warning(f"cleanup failed: {e}")

    return resp


if __name__ == "__main__":
    app.run(debug=True)
