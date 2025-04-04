from flask import Flask
from flask_cors import CORS
from .routes import api
from .models import db, Task
from .task_management import process_task
from .config import Config
import threading

# Create the Flask application
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5147"}})

    # Initialize the database
    db.init_app(app)

    # Register Blueprint for the routes
    app.register_blueprint(api, url_prefix='/api')

    # Create all database tables if not already created
    with app.app_context():
        db.create_all()

    # Create and start a background thread for task processing
    def start_processing_task():
        with app.app_context():  # Ensuring the app context is available in the thread
            # Fetch the task from the database
            task = Task.query.filter(Task.status == 'pending').first()  # Or modify to get a specific task
            if task:
                filters = task.filters  # Assuming task has a 'filters' attribute or method
                process_task(app, filters)  # Call process_task with the app context and filters

    # Start the background thread as a daemon thread
    thread = threading.Thread(target=start_processing_task, daemon=True)
    thread.start()

    return app
