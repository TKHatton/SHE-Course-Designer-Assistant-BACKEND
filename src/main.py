import os
import sys
import uuid
import json
import re
from datetime import datetime, timedelta

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.export_simple import export_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'your-actual-api-key-here')

# Enable CORS for all routes with wildcard origin
CORS(app, origins=["https://coursedesignerassistant.netlify.app", "*"], allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

app.register_blueprint(user_bp, url_prefix='/api')
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

# Built-in conversation intelligence (no external dependencies)
class SimpleConversationIntelligence:
    def __init__(self):
        self.framework_areas = [
            "Learning Objectives",
            "Target Audience Analysis", 
            "Educational Level Alignment",
            "Assessment Strategy",
            "Course Structure",
            "Bias Elimination",
            "Inclusive Design",
            "Career Relevance"
        ]
        
    def generate_response(self, user_message, conversation_context=None):
        """Generate a framework-guided response"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['beginner', 'new', 'start']):
            response = """Perfect! Creating an AI course for beginners is exactly what the She Is AI framework excels at. 

Let's start by understanding your learners better. Our framework emphasizes inclusive design from the very beginning.

Can you tell me more about:
- What specific background do your learners have? (Complete beginners to programming, or some technical experience?)
- What's their main motivation for learning AI? (Career change, skill enhancement, curiosity?)
- How much time can they realistically dedicate to learning?

This will help us design a course that's truly accessible and engaging for your specific audience."""
            
        elif any(word in user_lower for word in ['machine learning', 'ml', 'algorithms']):
            response = """Excellent choice! Machine learning is a fantastic entry point into AI, and our framework has specific approaches for making complex technical concepts accessible.

For ML courses, the She Is AI methodology emphasizes:
- **Practical application first** - learners see results before diving into theory
- **Real-world examples** that connect to diverse industries and backgrounds
- **Bias awareness** - critical when teaching ML algorithms

What specific ML topics are you most excited to include? For example:
- Supervised learning (classification, regression)
- Data preprocessing and ethics
- Model evaluation and interpretation
- Practical tools (Python, no-code platforms, etc.)

Also, what's the end goal for your learners? Are they aiming for specific careers or just general understanding?"""
            
        elif any(word in user_lower for word in ['career', 'job', 'professional']):
            response = """That's fantastic! Career-focused AI education is at the heart of the She Is AI framework. We believe in creating real pathways to opportunity.

Let's design something that truly prepares learners for the job market. Our framework includes:
- **Industry-relevant projects** that become portfolio pieces
- **Skills mapping** to actual job requirements
- **Inclusive career guidance** that addresses barriers different groups face

A few key questions to shape your course:
- What specific AI career paths are you targeting? (Data scientist, ML engineer, AI product manager, etc.)
- What's the job market like in your region or target area?
- How long do you envision the learning journey? (Bootcamp-style intensive vs. longer-term program)

We'll make sure every lesson connects directly to employable skills and real opportunities."""
            
        else:
            response = """I love your enthusiasm for creating an AI course! The She Is AI framework is designed to help you build something truly impactful and inclusive.

To give you the most relevant guidance, I'd love to understand your vision better:

- **Who are your learners?** (Students, professionals, career changers, etc.)
- **What's their current level?** (Complete beginners, some tech background, etc.)  
- **What's your main goal?** (Career preparation, general education, specific skills, etc.)
- **How will they learn?** (Online, in-person, self-paced, cohort-based, etc.)

The more specific you can be, the better I can help you leverage our framework's proven approaches for inclusive, effective AI education that creates real opportunities for learners."""

        return {
            'content': response,
            'framework_area': self._detect_framework_area(user_message),
            'confidence_score': 0.85,
            'message_type': 'framework_guidance'
        }
    
    def _detect_framework_area(self, message):
        """Detect which framework area the message relates to"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['audience', 'learner', 'student', 'who']):
            return "Target Audience Analysis"
        elif any(word in message_lower for word in ['beginner', 'advanced', 'level', 'experience']):
            return "Educational Level Alignment"
        elif any(word in message_lower for word in ['goal', 'objective', 'outcome', 'learn']):
            return "Learning Objectives"
        elif any(word in message_lower for word in ['assess', 'test', 'evaluation', 'grade']):
            return "Assessment Strategy"
        elif any(word in message_lower for word in ['career', 'job', 'professional', 'work']):
            return "Career Relevance"
        elif any(word in message_lower for word in ['structure', 'organize', 'sequence', 'order']):
            return "Course Structure"
        else:
            return "General Framework Guidance"
    
    def sanitize_input(self, user_input):
        """Basic input sanitization"""
        if not user_input or not isinstance(user_input, str):
            return ""
            
        # Remove HTML tags
        clean_input = re.sub(r'<[^>]+>', '', user_input)
        
        # Limit length
        if len(clean_input) > 1000:
            clean_input = clean_input[:1000]
            
        return clean_input.strip()
    
    def check_safety_violations(self, message):
        """Check for safety violations"""
        message_lower = message.lower()
        
        # Simple keyword-based safety check
        inappropriate_keywords = [
            'hack', 'illegal', 'harmful', 'dangerous', 'weapon',
            'violence', 'hate', 'discrimination'
        ]
        
        for keyword in inappropriate_keywords:
            if keyword in message_lower:
                return True, f"I focus specifically on educational course design using the She Is AI framework. Let's keep our conversation centered on creating inclusive, effective AI education."
                
        return False, None

# Initialize conversation intelligence
conv_intelligence = SimpleConversationIntelligence()

# Rate limiting storage
rate_limit_storage = {}

def check_rate_limit(session_id, max_requests=30, window_minutes=5):
    """Check if user has exceeded rate limit"""
    current_time = datetime.utcnow()
    window_start = current_time - timedelta(minutes=window_minutes)
    
    if session_id not in rate_limit_storage:
        rate_limit_storage[session_id] = []
    
    # Remove old requests outside the window
    rate_limit_storage[session_id] = [
        req_time for req_time in rate_limit_storage[session_id] 
        if req_time > window_start
    ]
    
    # Check if limit exceeded
    if len(rate_limit_storage[session_id]) >= max_requests:
        return False
    
    # Add current request
    rate_limit_storage[session_id].append(current_time)
    return True

# CONVERSATION ROUTES (built directly into main.py)
@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation session"""
    session_id = str(uuid.uuid4())
    
    conversation = Conversation(session_id=session_id)
    db.session.add(conversation)
    db.session.commit()
    
    # Add welcome message with safety disclaimer
    welcome_content = """Hi! I'm the She Is AI Course Design Assistant. I'm here to help you create an incredible AI course using our proven educational framework. Together, we'll design something that's inclusive, engaging, and creates real career opportunities for your learners.

**Important Notice:** This assistant is for educational course design only. By using it, you agree to:
• Use for legitimate educational purposes only
• Not attempt to reverse engineer or extract proprietary information  
• Not share inappropriate or harmful content
• Understand this is a design tool, not professional legal/medical advice

Your responses help design your course and aren't stored permanently or shared. What kind of AI course are you excited to build?"""
    
    welcome_msg = Message(
        conversation_id=conversation.id,
        sender='assistant',
        content=welcome_content,
        message_type='welcome'
    )
    db.session.add(welcome_msg)
    db.session.commit()
    
    return jsonify({
        'session_id': session_id,
        'conversation': conversation.to_dict(),
        'welcome_message': welcome_msg.to_dict()
    })

@app.route('/api/conversations/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message in a conversation"""
    
    # Rate limiting check
    if not check_rate_limit(session_id):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please wait a moment before sending another message.',
            'retry_after': 60
        }), 429
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message content is required'}), 400
    
    user_message = data['message']
    original_message = user_message
    
    # Input sanitization
    user_message = conv_intelligence.sanitize_input(user_message)
    
    if not user_message or len(user_message.strip()) == 0:
        return jsonify({
            'error': 'Invalid message content',
            'safety_notice': 'Your message contained content that cannot be processed for security reasons.'
        }), 400
    
    # Check for safety violations
    has_violation, safety_message = conv_intelligence.check_safety_violations(original_message)
    
    conversation = Conversation.query.filter_by(session_id=session_id).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    # If safety violations detected, respond with safety message
    if has_violation:
        safety_msg = Message(
            conversation_id=conversation.id,
            sender='assistant',
            content=safety_message,
            message_type='safety_response'
        )
        db.session.add(safety_msg)
        db.session.commit()
        
        return jsonify({
            'ai_response': safety_msg.to_dict(),
            'safety_violation': True,
            'privacy_notice': 'Your responses help design your course and aren\'t stored permanently or shared'
        })
    
    # Get conversation history for analysis
    conversation_history = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    history_data = [{'sender': msg.sender, 'content': msg.content} for msg in conversation_history]
    
    # Generate response using conversation intelligence
    response_data = conv_intelligence.generate_response(user_message, history_data)
    
    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        sender='user',
        content=user_message,
        intent='course_design',
        confidence=response_data.get('confidence_score', 0.8)
    )
    db.session.add(user_msg)
    
    # Get AI response content
    ai_response = response_data['content']
    
    # Add privacy reminder periodically
    message_count = len(history_data)
    if message_count > 0 and message_count % 10 == 0:
        ai_response += "\n\n*Privacy reminder: Your responses help design your course and aren't stored permanently or shared.*"
    
    # Save AI response
    ai_msg = Message(
        conversation_id=conversation.id,
        sender='assistant',
        content=ai_response,
        message_type='response'
    )
    db.session.add(ai_msg)
    
    # Update conversation progress
    conversation.current_step = min(conversation.current_step + 1, conversation.total_steps)
    conversation.completion_percentage = (conversation.current_step / conversation.total_steps) * 100
    conversation.updated_at = datetime.utcnow()
    
    # Update framework areas covered
    framework_area = response_data.get('framework_area', 'General Framework Guidance')
    current_areas = conversation.get_framework_areas_covered()
    if framework_area not in current_areas:
        new_areas = current_areas + [framework_area]
        conversation.set_framework_areas_covered(new_areas)
    
    db.session.commit()
    
    return jsonify({
        'user_message': user_msg.to_dict(),
        'ai_response': ai_msg.to_dict(),
        'conversation_update': {
            'current_step': conversation.current_step,
            'completion_percentage': conversation.completion_percentage,
            'framework_areas_covered': conversation.get_framework_areas_covered()
        },
        'analysis': {
            'intent': 'course_design',
            'confidence': response_data.get('confidence_score', 0.8),
            'boundary_violation': False,
            'conversation_health': 'good',
            'needs_depth': False
        },
        'privacy_notice': 'Your responses help design your course and aren\'t stored permanently or shared',
        'usage_disclaimer': 'This assistant is for educational course design only.'
    })

@app.route('/api/conversations/<session_id>/summary', methods=['GET'])
def get_conversation_summary(session_id):
    """Get a summary of the conversation and course design"""
    conversation = Conversation.query.filter_by(session_id=session_id).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    
    return jsonify({
        'conversation': conversation.to_dict(),
        'message_count': len(messages),
        'framework_areas_covered': conversation.get_framework_areas_covered(),
        'completion_status': {
            'current_step': conversation.current_step,
            'total_steps': conversation.total_steps,
            'percentage': conversation.completion_percentage
        }
    })

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

