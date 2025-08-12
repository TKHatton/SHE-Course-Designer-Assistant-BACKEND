import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.conversation import conversation_bp
from src.routes.export_simple import export_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes with wildcard origin
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(conversation_bp, url_prefix='/api')
app.register_blueprint(export_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import all models to ensure they're registered
from src.models.conversation import Conversation, Message, FrameworkConcept

db.init_app(app)

def initialize_database():
    """Initialize database and seed data"""
    with app.app_context():
        db.create_all()
        # Seed framework concepts if not already present
        if FrameworkConcept.query.count() == 0:
            from src.utils.seed_data import seed_framework_concepts
            seed_framework_concepts()

# Initialize database
initialize_database()

@app.route('/health')
def health_check():
    return {"status": "healthy", "message": "She Is AI Assistant API is running"}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
