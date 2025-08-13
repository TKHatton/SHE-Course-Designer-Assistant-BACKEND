from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime
import openai

app = Flask(__name__)

# CORS configuration
CORS(app, origins=[
    "https://coursedesignerassistant.netlify.app",
    "http://localhost:3000",
    "http://localhost:5173"
])

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')

# In-memory storage for conversations
conversations = {}

# Simple conversation flow - ask questions in order, then summarize
CONVERSATION_FLOW = [
    {
        "step": 1,
        "question": "Who are your learners? (students, professionals, career changers, etc.)",
        "key": "learners"
    },
    {
        "step": 2,
        "question": "What specific AI tools or platforms will you focus on?",
        "key": "tools"
    },
    {
        "step": 3,
        "question": "What are the main learning goals for your course?",
        "key": "goals"
    },
    {
        "step": 4,
        "question": "How will you assess or evaluate student learning?",
        "key": "assessment"
    },
    {
        "step": 5,
        "question": "What teaching methods will you use to keep learners engaged?",
        "key": "methods"
    }
]

def get_conversation_step(conversation):
    """Get the current step in the conversation flow"""
    messages = conversation.get('messages', [])
    user_responses = [msg for msg in messages if msg.get('sender') == 'user']
    
    # Start at step 1, advance based on user responses
    current_step = len(user_responses) + 1
    
    # Cap at max steps
    if current_step > len(CONVERSATION_FLOW):
        return None  # Time to summarize
    
    return current_step

def extract_user_responses(conversation):
    """Extract user responses for each step"""
    messages = conversation.get('messages', [])
    user_responses = [msg.get('content', '') for msg in messages if msg.get('sender') == 'user']
    
    responses = {}
    for i, response in enumerate(user_responses):
        if i < len(CONVERSATION_FLOW):
            key = CONVERSATION_FLOW[i]['key']
            responses[key] = response
    
    return responses

def should_end_conversation(conversation):
    """Simple check - end after 5 user responses or if user signals completion"""
    messages = conversation.get('messages', [])
    user_responses = [msg for msg in messages if msg.get('sender') == 'user']
    
    # Check for completion signals in last message
    if user_responses:
        last_message = user_responses[-1].get('content', '').lower()
        completion_signals = ['wrap up', 'summary', 'done', 'finish', 'end this', 'conclude']
        if any(signal in last_message for signal in completion_signals):
            return True
    
    # End after 5 responses
    return len(user_responses) >= 5

def generate_course_summary(responses):
    """Generate a real summary based on actual user responses"""
    
    learners = responses.get('learners', 'Not specified')
    tools = responses.get('tools', 'Not specified')
    goals = responses.get('goals', 'Not specified')
    assessment = responses.get('assessment', 'Not specified')
    methods = responses.get('methods', 'Not specified')
    
    summary = f"""🎉 **Excellent! You've outlined a solid AI course design!**

## **Your Course Design:**

**🎯 Target Learners:** {learners}
**🛠️ AI Tools/Platforms:** {tools}
**📈 Learning Goals:** {goals}
**📊 Assessment Approach:** {assessment}
**👩‍🏫 Teaching Methods:** {methods}

## **Framework Alignment:**

Your course design incorporates key She Is AI principles:
✅ **Clear learner focus** - You've identified your specific audience
✅ **Practical AI tools** - Hands-on experience with real platforms
✅ **Defined outcomes** - Clear goals for student achievement
✅ **Thoughtful assessment** - Meaningful evaluation methods
✅ **Engaging pedagogy** - Active learning approaches

## **Next Steps:**

🔄 **Export Your Design** - Use the Export button to download your course outline
📋 **Refine Details** - Add specific lesson plans and timelines
🚀 **Implement** - You have a solid foundation to build from

**Your course is ready for development! Well done creating a learner-centered AI education experience.**"""

    return summary

def detect_bias_or_exclusion(message):
    """Check for exclusionary or biased language"""
    message_lower = message.lower()
    
    exclusionary_patterns = [
        "only for", "not for", "can't handle", "too difficult for",
        "not smart enough", "exclude", "not suitable for"
    ]
    
    has_bias = any(pattern in message_lower for pattern in exclusionary_patterns)
    
    if has_bias:
        return "I notice some language that might exclude certain learners. The She Is AI framework emphasizes inclusive design that welcomes all learners. How can we make your course more accessible and inclusive?"
    
    return None

def get_next_question(conversation):
    """Get the next question in the conversation flow"""
    current_step = get_conversation_step(conversation)
    
    if current_step is None or current_step > len(CONVERSATION_FLOW):
        # Time to summarize
        responses = extract_user_responses(conversation)
        return generate_course_summary(responses)
    
    # Get the question for current step
    flow_item = CONVERSATION_FLOW[current_step - 1]
    return flow_item['question']

def check_safety_violations(message):
    """Check for inappropriate content"""
    inappropriate_keywords = [
        'personal advice', 'relationship', 'medical', 'legal advice', 
        'politics', 'religion', 'inappropriate', 'harmful'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in inappropriate_keywords)

def get_safety_response():
    """Return appropriate response for safety violations"""
    return {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": "I specialize exclusively in the She Is AI framework to give you the best course design guidance possible. Let's focus on creating your AI education course. What specific aspect of course design would you like to explore?",
        "timestamp": datetime.now().isoformat(),
        "message_type": "safety_redirect"
    }

def calculate_progress(conversation):
    """Calculate accurate progress based on conversation flow"""
    messages = conversation.get('messages', [])
    user_responses = [msg for msg in messages if msg.get('sender') == 'user']
    
    current_step = len(user_responses)
    total_steps = len(CONVERSATION_FLOW)
    
    return {
        'current_step': min(current_step, total_steps),
        'total_steps': total_steps,
        'completion_percentage': min(100, int((current_step / total_steps) * 100)),
        'framework_areas_covered': [f"Step {i+1}" for i in range(min(current_step, total_steps))]
    }

def create_recovery_conversation(session_id, user_message):
    """Create a new conversation when session is lost"""
    conversation = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'recovered_session': True
    }
    
    conversations[session_id] = conversation
    
    # Add user message
    user_msg = {
        "id": str(uuid.uuid4()),
        "sender": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    }
    conversation['messages'].append(user_msg)
    
    # Create recovery message and continue with next question
    recovery_content = "Welcome back! I'm here to help you design your AI course. "
    
    # Get next question based on the message they sent
    next_question = get_next_question(conversation)
    if "🎉" in next_question:  # It's a summary
        recovery_content = next_question
    else:
        recovery_content += f"Let's continue: {next_question}"
    
    recovery_message = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": recovery_content,
        "timestamp": datetime.now().isoformat(),
        "message_type": "session_recovery"
    }
    
    conversation['messages'].append(recovery_message)
    
    return conversation, recovery_message

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "message": "She Is AI Assistant API is running",
        "status": "healthy",
        "active_conversations": len(conversations)
    })

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Initialize a new conversation"""
    session_id = str(uuid.uuid4())
    
    conversation = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': []
    }
    
    conversations[session_id] = conversation
    
    # Start with first question
    first_question = CONVERSATION_FLOW[0]['question']
    
    welcome_message = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": f"Hi! I'm the She Is AI Course Design Assistant. I'll help you create an AI course using our framework.\n\nI'll ask you 5 focused questions to understand your course design, then provide a comprehensive summary.\n\nLet's start: {first_question}",
        "timestamp": datetime.now().isoformat(),
        "message_type": "welcome"
    }
    
    conversation['messages'].append(welcome_message)
    progress = calculate_progress(conversation)
    
    return jsonify({
        "session_id": session_id,
        "welcome_message": welcome_message,
        "conversation": progress
    })

@app.route('/api/conversations/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message with simple, reliable conversation flow"""
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # Handle missing sessions with recovery
    if session_id not in conversations:
        print(f"Session {session_id} not found - creating recovery conversation")
        conversation, recovery_message = create_recovery_conversation(session_id, message)
        
        return jsonify({
            "ai_response": recovery_message,
            "safety_violation": False,
            "session_recovered": True,
            "conversation_update": calculate_progress(conversation)
        })
    
    conversation = conversations[session_id]
    
    # Add user message
    user_message = {
        "id": str(uuid.uuid4()),
        "sender": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    }
    conversation['messages'].append(user_message)
    
    # Check safety
    if check_safety_violations(message):
        safety_response = get_safety_response()
        conversation['messages'].append(safety_response)
        
        return jsonify({
            "ai_response": safety_response,
            "safety_violation": True,
            "session_recovered": False,
            "conversation_update": calculate_progress(conversation)
        })
    
    # Check for bias/exclusion
    bias_response = detect_bias_or_exclusion(message)
    if bias_response:
        ai_response = {
            "id": str(uuid.uuid4()),
            "sender": "assistant",
            "content": bias_response,
            "timestamp": datetime.now().isoformat(),
            "message_type": "bias_correction"
        }
        conversation['messages'].append(ai_response)
        
        return jsonify({
            "ai_response": ai_response,
            "safety_violation": False,
            "session_recovered": False,
            "conversation_update": calculate_progress(conversation)
        })
    
    # Check if conversation should end
    if should_end_conversation(conversation):
        responses = extract_user_responses(conversation)
        ai_content = generate_course_summary(responses)
    else:
        # Get next question
        ai_content = get_next_question(conversation)
    
    ai_response = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": ai_content,
        "timestamp": datetime.now().isoformat(),
        "message_type": "framework_guidance"
    }
    
    conversation['messages'].append(ai_response)
    updated_progress = calculate_progress(conversation)
    
    return jsonify({
        "ai_response": ai_response,
        "safety_violation": False,
        "session_recovered": False,
        "conversation_update": updated_progress
    })

@app.route('/api/conversations/<session_id>/export', methods=['GET'])
def export_conversation(session_id):
    """Export conversation data"""
    if session_id not in conversations:
        return jsonify({
            "error": "Conversation not found",
            "session_id": session_id,
            "recovery_available": True
        }), 404
    
    conversation = conversations[session_id]
    responses = extract_user_responses(conversation)
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify({
            "session_id": session_id,
            "conversation": conversation,
            "course_responses": responses,
            "framework_progress": calculate_progress(conversation),
            "export_timestamp": datetime.now().isoformat()
        })
    
    elif format_type == 'csv':
        csv_data = "Question,Response\n"
        for i, response in enumerate(responses.values()):
            if i < len(CONVERSATION_FLOW):
                question = CONVERSATION_FLOW[i]['question']
                csv_data += f"\"{question}\",\"{response}\"\n"
        
        return csv_data, 200, {'Content-Type': 'text/csv'}
    
    else:
        return jsonify({"error": "Unsupported format"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/health",
            "/api/conversations",
            "/api/conversations/<session_id>/messages",
            "/api/conversations/<session_id>/export"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "The server encountered an unexpected condition. Please try again."
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

