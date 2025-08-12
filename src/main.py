import uuid
from flask import jsonify, request

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.conversation import conversation_bp  # ← THIS LINE
from src.routes.export_simple import export_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['OPENAI_API_KEY'] = 'your-actual-api-key-here'

CORS(app, origins=["https://coursedesignerassistant.netlify.app", "*"], allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"] )

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(conversation_bp, url_prefix='/api')  # ← THIS LINE
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

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    session_id = str(uuid.uuid4())
    return jsonify({
        'session_id': session_id,
        'welcome_message': {
            'content': "Hi! I'm the She Is AI Course Design Assistant. What kind of AI course are you excited to build?",
            'sender': 'assistant'
        }
    })

@app.route('/api/conversations/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    data = request.get_json()
    user_message = data.get('message', '')
    
    response = f"Thanks for sharing: '{user_message}'. I'm here to help you design an amazing AI course using the She Is AI's educational framework. Can you tell me more about your target audience?"
    
    return jsonify({
        'ai_response': {
            'content': response,
            'sender': 'assistant'
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
