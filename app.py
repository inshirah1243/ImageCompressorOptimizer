import os
import uuid

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-for-production")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Return True only for supported image extensions."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def compress_image(source_path, destination_path, extension, quality):
    """Save an optimized copy of an image using Pillow."""
    with Image.open(source_path) as image:
        if extension in {"jpg", "jpeg"}:
            # JPEG cannot store transparency or palette-only images.
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            image.save(destination_path, "JPEG", quality=quality, optimize=True)
        else:
            # Pillow's PNG compression level is 0-9 (9 = smallest, slowest).
            compression_level = max(0, min(9, round((100 - quality) * 9 / 100)))
            image.save(destination_path, "PNG", optimize=True, compress_level=compression_level)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        uploaded_file = request.files.get("image")
        quality_text = request.form.get("quality", "75")

        if not uploaded_file or uploaded_file.filename == "":
            flash("Please choose an image to upload.")
            return redirect(url_for("index"))
        if not allowed_file(uploaded_file.filename):
            flash("Only JPG, JPEG, and PNG files are supported.")
            return redirect(url_for("index"))

        try:
            quality = int(quality_text)
            if not 1 <= quality <= 100:
                raise ValueError
        except ValueError:
            flash("Quality must be a number from 1 to 100.")
            return redirect(url_for("index"))

        safe_name = secure_filename(uploaded_file.filename)
        extension = safe_name.rsplit(".", 1)[1].lower()
        unique_id = uuid.uuid4().hex
        original_name = f"{unique_id}_original.{extension}"
        compressed_name = f"{unique_id}_compressed.{extension}"
        original_path = os.path.join(app.config["UPLOAD_FOLDER"], original_name)
        compressed_path = os.path.join(app.config["UPLOAD_FOLDER"], compressed_name)

        uploaded_file.save(original_path)
        try:
            compress_image(original_path, compressed_path, extension, quality)
        except (UnidentifiedImageError, OSError):
            if os.path.exists(original_path):
                os.remove(original_path)
            flash("That file could not be read as a valid image.")
            return redirect(url_for("index"))

        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(compressed_path)
        reduction = (1 - compressed_size / original_size) * 100 if original_size else 0
        result = {
            "original_size": original_size,
            "compressed_size": compressed_size,
            "reduction": reduction,
            "download_url": url_for("download", filename=compressed_name),
            "download_name": f"compressed_{safe_name}",
        }

    return render_template("index.html", result=result)


@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename, as_attachment=True, download_name=filename
    )


@app.errorhandler(413)
def file_too_large(_error):
    flash("File is too large. The maximum upload size is 16 MB.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
