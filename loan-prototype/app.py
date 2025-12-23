from flask import Flask, render_template, request, url_for
import uuid
import os
from werkzeug.utils import secure_filename

from config import Config
from event_bus.kafka_client import publish
from database.db import init_db, save_application, get_application

# Import services to initialize
import services.commercial_service as commercial_service
import services.risk_service as risk_service
import services.credit_service as credit_service
import services.notification_service as notification_service

app = Flask(__name__)
app.config.from_object(Config)

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize DB
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        app_id = str(uuid.uuid4())
        name = request.form.get('name', 'Unknown')

        files = request.files.getlist('documents')
        saved_paths = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], f"{app_id}_{filename}")
                file.save(path)
                saved_paths.append(path)

        data = {
            "app_id": app_id,
            "name": name,
            "documents": saved_paths
        }

        save_application(app_id, data)
        publish(Config.TOPICS["submitted"], data)

        return f'''
            Application submitted!<br>
            Your ID: <strong>{app_id}</strong><br><br>
            <a href="/status/{app_id}">Check Status</a>
        '''

    return render_template("apply.html")

@app.route("/status/<app_id>")
def status(app_id):
    app_data = get_application(app_id)
    if not app_data:
        return "Application not found", 404
    return render_template("status.html", **app_data)

if __name__ == "__main__":
    # Initialize all services
    commercial_service.init()
    risk_service.init()
    credit_service.init()
    notification_service.init()

    app.run(debug=True)