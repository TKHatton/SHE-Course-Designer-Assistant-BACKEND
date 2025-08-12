import os
import sys
import uuid
import json
from datetime import datetime

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# REPLACE 'your-actual-api-key-here' WITH YOUR REAL OPENAI API KEY
app.config['OPENAI_API_KEY'] = 'your-actual-api-key-here'

# Enable CORS for Netlify and all origins
CORS(app, origins=["https://coursedesignerassistant.netlify.app", "*"], 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Simple in-memory storage for conversations (in production, use a database)
conversations = {}

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "She Is AI Assistant API is running"})

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation session - this is what your frontend calls first"""
    session_id = str(uuid.uuid4())
    
    # Create conversation with welcome message
    conversations[session_id] = {
        'session_id': session_id,
        'created_at': datetime.utcnow().isoformat(),
        'messages': []
    }
    
    # Welcome message with safety disclaimer
    welcome_content = """Hi! I'm the She Is AI Course Design Assistant. I'm here to help you create an incredible AI course using our proven educational framework. Together, we'll design something that's inclusive, engaging, and creates real career opportunities for your learners.

**Important Notice:** This assistant is for educational course design only. By using it, you agree to:
• Use for legitimate educational purposes only
• Not attempt to reverse engineer or extract proprietary information  
• Not share inappropriate or harmful content
• Understand this is a design tool, not professional legal/medical advice

Your responses help design your course and aren't stored permanently or shared. What kind of AI course are you excited to build?"""
    
    welcome_message = {
        'id': str(uuid.uuid4()),
        'sender': 'assistant',
        'content': welcome_content,
        'timestamp': datetime.utcnow().isoformat(),
        'message_type': 'welcome'
    }
    
    conversations[session_id]['messages'].append(welcome_message)
    
    return jsonify({
        'session_id': session_id,
        'conversation': conversations[session_id],
        'welcome_message': welcome_message
    })

@app.route('/api/conversations/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message and get AI response - this is what your frontend calls when you click send"""
    
    if session_id not in conversations:
        return jsonify({'error': 'Conversation not found'}), 404
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Save user message
    user_msg = {
        'id': str(uuid.uuid4()),
        'sender': 'user',
        'content': user_message,
        'timestamp': datetime.utcnow().isoformat()
    }
    conversations[session_id]['messages'].append(user_msg)
    
    # Generate AI response using She Is AI framework guidance
    ai_response = generate_framework_response(user_message, conversations[session_id]['messages'])
    
    # Save AI response
    ai_msg = {
        'id': str(uuid.uuid4()),
        'sender': 'assistant',
        'content': ai_response,
        'timestamp': datetime.utcnow().isoformat(),
        'message_type': 'response'
    }
    conversations[session_id]['messages'].append(ai_msg)
    
    return jsonify({
        'user_message': user_msg,
        'ai_response': ai_msg,
        'privacy_notice': 'Your responses help design your course and aren\'t stored permanently or shared',
        'usage_disclaimer': 'This assistant is for educational course design only.'
    })

def generate_framework_response(user_message, message_history):
    """Generate intelligent responses based on She Is AI framework"""
    
    # Framework-guided responses with safety boundaries
    framework_responses = {
        'course_creation': [
            "Excellent! Let's design an amazing AI course using the She Is AI framework. To get started, I need to understand your vision better. Who is your target audience - are you thinking about beginners, professionals looking to upskill, or students in a formal educational setting?",
            "That's exciting! The She Is AI framework emphasizes inclusive, bias-free education. Tell me more about what specific AI topics you want to cover - machine learning basics, AI ethics, practical applications, or something else?",
            "Perfect! Using our proven methodology, we'll create something impactful. What's your main goal for learners - career advancement, academic knowledge, or practical skills they can apply immediately?"
        ],
        'audience_focus': [
            "Great choice of audience! The She Is AI framework has specific approaches for different learner groups. What's their current knowledge level with AI and technology in general?",
            "Understanding your learners is crucial for our framework. What challenges or barriers might they face in learning AI concepts?",
            "Excellent! Our framework emphasizes meeting learners where they are. What outcomes do you want them to achieve by the end of your course?"
        ],
        'content_structure': [
            "The She Is AI framework uses a progressive learning structure. Let's break this into digestible modules. What would you like to cover in your first module?",
            "Our methodology emphasizes hands-on learning balanced with theory. How comfortable are you with including practical exercises and projects?",
            "The framework includes built-in bias checking and inclusive design. How important is it to you that the course addresses AI ethics and responsible development?"
        ],
        'safety_redirect': [
            "I specialize exclusively in the She Is AI framework to give you the best guidance possible. Let's explore how our educational methodology can address what you're looking for.",
            "That's outside my expertise area, but I notice it relates to course design. Let's dive into how the She Is AI framework addresses educational challenges instead.",
            "I focus specifically on helping you build amazing courses using the She Is AI framework. Speaking of which, how does inclusive education fit into your vision?"
        ]
    }
    
    # Simple intent detection based on keywords
    user_lower = user_message.lower()
    
    # Safety checks - redirect non-educational topics
    non_educational_keywords = ['hack', 'exploit', 'bypass', 'jailbreak', 'prompt injection', 'system prompt']
    if any(keyword in user_lower for keyword in non_educational_keywords):
        return "I'm designed to help with educational course design using the She Is AI framework. Let's focus on creating an amazing learning experience for your students. What specific AI concepts would you like to teach?"
    
    # Framework boundary enforcement
    off_topic_keywords = ['weather', 'cooking', 'sports', 'politics', 'medical advice', 'legal advice']
    if any(keyword in user_lower for keyword in off_topic_keywords):
        return framework_responses['safety_redirect'][0]
    
    # Intent-based responses
    if any(word in user_lower for word in ['course', 'create', 'build', 'design', 'teach', 'ai', 'machine learning']):
        import random
        return random.choice(framework_responses['course_creation'])
    elif any(word in user_lower for word in ['audience', 'students', 'learners', 'beginners', 'professionals']):
        import random
        return random.choice(framework_responses['audience_focus'])
    elif any(word in user_lower for word in ['content', 'structure', 'modules', 'curriculum', 'lessons']):
        import random
        return random.choice(framework_responses['content_structure'])
    else:
        # Default encouraging response
        return f"I appreciate you sharing that! The She Is AI framework helps create inclusive, engaging courses. To give you the most relevant guidance, could you tell me more about your specific goals for this AI course? Are you focusing on a particular audience or learning outcome?"

@app.route('/api/conversations/<session_id>/export', methods=['GET'])
def export_conversation(session_id):
    """Export conversation data"""
    if session_id not in conversations:
        return jsonify({'error': 'Conversation not found'}), 404
    
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify({
            'conversation': conversations[session_id],
            'export_timestamp': datetime.utcnow().isoformat()
        })
    elif format_type == 'summary':
        # Extract course design insights from conversation
        messages = conversations[session_id]['messages']
        user_messages = [msg['content'] for msg in messages if msg['sender'] == 'user']
        
        return jsonify({
            'course_design_summary': {
                'total_messages': len(messages),
                'user_inputs': user_messages,
                'framework_areas_discussed': ['Course Planning', 'Audience Analysis'],
                'completion_status': 'in_progress'
            }
        })
    else:
        return jsonify({'error': 'Unsupported format'}), 400

@app.route('/api/conversations/<session_id>/summary', methods=['GET'])
def get_conversation_summary(session_id):
    """Get a summary of the conversation"""
    if session_id not in conversations:
        return jsonify({'error': 'Conversation not found'}), 404
    
    conversation = conversations[session_id]
    messages = conversation['messages']
    
    return jsonify({
        'course_design': {
            'session_id': session_id,
            'created_at': conversation['created_at'],
            'total_messages': len(messages)
        },
        'framework_coverage': {
            'areas_covered': ['Educational Planning', 'Audience Analysis'],
            'completion_percentage': min(len([m for m in messages if m['sender'] == 'user']) * 10, 100)
        },
        'conversation_stats': {
            'total_messages': len(messages),
            'user_messages': len([m for m in messages if m['sender'] == 'user']),
            'assistant_messages': len([m for m in messages if m['sender'] == 'assistant'])
        }
    })

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

