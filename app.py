from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)

# Configuration for upload folder and allowed file types
UPLOAD_FOLDER = "/path/to/uploaded"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Discord webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/******"

@app.route("/submit-content", methods=["GET", "POST"])
def submit_content():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        files = request.files.getlist("files")

        if not description:
            return jsonify({"status": "error", "message": "Description is required."}), 400

        if len(files) > 4:
            return jsonify({"status": "error", "message": "You can upload a maximum of 4 files."}), 400

        # Create a directory based on the description
        description_dir = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(description))
        os.makedirs(description_dir, exist_ok=True)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(description_dir, filename))

        # Send a notification to Discord
        webhook_data = {
            "content": f"New content submitted: **{description}**\nNumber of files: {len(files)}"
        }
        try:
            requests.post(DISCORD_WEBHOOK_URL, json=webhook_data)
        except Exception as e:
            print(f"Error sending Discord webhook: {e}")

        return jsonify({"status": "success", "message": "Files successfully uploaded!"})

    return render_template("submit_content.html")
