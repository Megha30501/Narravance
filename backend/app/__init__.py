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

    # Enable CORS for specific frontend URL
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5147"}})

    # Initialize the database
    db.init_app(app)

    # Register Blueprint for the routes
    app.register_blueprint(api, url_prefix='/api')

    # Create all database tables if not already created
    with app.app_context():
        db.create_all()

    # Function to start processing a task in the background
    def start_processing_task():
        with app.app_context():  # Ensuring the app context is available in the thread
            # Fetch the first pending task from the database
            task = Task.query.filter(Task.status == 'pending').first()  # Modify as needed for more specific filtering
            if task:
                filters = task.filters  # Assuming task has a 'filters' attribute or method
                process_task(task.id)  # Pass task ID or use filters as needed for processing

    # Start the background thread to process tasks
    thread = threading.Thread(target=start_processing_task, daemon=True)
    thread.start()

    return app
