from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime
import openai

app = Flask(__name__)

# CORS configuration - allow your frontend domains
CORS(app, origins=[
    "https://coursedesignerassistant.netlify.app",
    "http://localhost:3000",
    "http://localhost:5173"
])

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')

# In-memory storage for conversations (use database in production)
conversations = {}

# She Is AI Framework Areas - COMPLETE FRAMEWORK
FRAMEWORK_AREAS = [
    {
        "name": "Learner Understanding",
        "questions": [
            "Who are your learners? (students, professionals, career changers, etc.)",
            "What's their current level? (complete beginners, some tech background, etc.)",
            "What are their main goals? (career preparation, general education, specific skills, etc.)"
        ]
    },
    {
        "name": "AI in Context",
        "questions": [
            "How will AI shape your learners' field/topic? (tools, workflows, industry examples)",
            "What specific AI applications are most relevant to your subject area?",
            "How can you make AI concepts tangible and relatable to your learners?"
        ]
    },
    {
        "name": "Ethics & Responsible AI Use",
        "questions": [
            "What ethical considerations are most important for your learners to understand?",
            "How will you help them design safe, fair, and trustworthy AI experiences?",
            "What real-world examples of AI ethics can you incorporate?"
        ]
    },
    {
        "name": "Bias Recognition & Equity",
        "questions": [
            "How will you help learners spot bias in AI systems?",
            "What strategies will you teach for designing equitable AI systems?",
            "How will you address bias in your own course design and delivery?"
        ]
    },
    {
        "name": "AI Skills for the Future",
        "questions": [
            "What specific AI-related skills will your learners develop for career readiness?",
            "How will you connect these skills to real job opportunities?",
            "What hands-on projects will demonstrate these skills?"
        ]
    },
    {
        "name": "Women's Role in Shaping AI",
        "questions": [
            "How will you highlight contributions and leadership of women in AI?",
            "What role models and success stories will you share?",
            "How will you encourage all learners to see themselves as AI leaders?"
        ]
    },
    {
        "name": "Assessment Strategy",
        "questions": [
            "How will you assess learning through authentic, portfolio-based evaluation?",
            "What real-world applications will learners create to demonstrate knowledge?",
            "How will peer evaluation and collaborative assessment be integrated?"
        ]
    },
    {
        "name": "Universal Lesson Structure",
        "questions": [
            "How will you implement the 7-component lesson structure in your context?",
            "What opening rituals and community-building activities will you use?",
            "How will you balance content delivery with hands-on practice?"
        ]
    },
    {
        "name": "Content Progression",
        "questions": [
            "How will you sequence content to build from foundational to advanced concepts?",
            "What scaffolding will you provide for different learning levels?",
            "How will you ensure all five core AI concepts are covered appropriately?"
        ]
    },
    {
        "name": "Course Implementation",
        "questions": [
            "What resources and support will you need to implement this course?",
            "How will you measure success and gather feedback for improvement?",
            "What's your plan for launching and sustaining this course?"
        ]
    }
]

def get_ai_response(message, conversation_context, current_area, progress):
    """Generate AI response using OpenAI with She Is AI framework guidance"""
    
    # Build context for the AI
    system_prompt = f"""You are the She Is AI Course Design Assistant, helping educators create inclusive, bias-free AI education courses.

CURRENT FRAMEWORK AREA: {current_area['name']}
PROGRESS: {progress['current_step']}/{progress['total_steps']} areas completed

Your role is to:
1. Guide users through the She Is AI framework systematically
2. Ask ONE focused question at a time from the current framework area
3. Provide brief, actionable guidance (2-3 sentences max)
4. Keep responses concise and conversational
5. Move to the next area only when current area is sufficiently explored

FRAMEWORK AREAS TO COVER:
{json.dumps([area['name'] for area in FRAMEWORK_AREAS], indent=2)}

CURRENT QUESTIONS FOR {current_area['name']}:
{json.dumps(current_area['questions'], indent=2)}

CONVERSATION HISTORY:
{json.dumps(conversation_context[-3:], indent=2) if conversation_context else "No previous messages"}

Guidelines:
- Be concise and actionable (avoid long explanations)
- Ask ONE specific question to move the conversation forward
- Provide brief context or tips when helpful
- Stay focused on course design using the She Is AI framework
- Redirect off-topic conversations gently back to course design
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=200,  # Keep responses concise
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return f"I'm having trouble connecting right now. Let's continue with {current_area['name']} - {current_area['questions'][0]}"

def check_safety_violations(message):
    """Check for inappropriate content or off-topic requests"""
    
    # Simple keyword-based safety check
    inappropriate_keywords = [
        'personal advice', 'relationship', 'medical', 'legal advice', 
        'politics', 'religion', 'inappropriate', 'harmful'
    ]
    
    message_lower = message.lower()
    
    for keyword in inappropriate_keywords:
        if keyword in message_lower:
            return True
    
    # Check if completely off-topic from education/course design
    education_keywords = [
        'course', 'learn', 'teach', 'student', 'education', 'curriculum',
        'lesson', 'training', 'skill', 'knowledge', 'ai', 'framework'
    ]
    
    has_education_context = any(keyword in message_lower for keyword in education_keywords)
    
    if len(message.split()) > 10 and not has_education_context:
        return True
    
    return False

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
    """Calculate progress through the framework areas"""
    areas_covered = len(conversation.get('framework_areas_covered', []))
    total_areas = len(FRAMEWORK_AREAS)
    
    return {
        'current_step': areas_covered + 1,
        'total_steps': total_areas,
        'completion_percentage': min(100, int((areas_covered / total_areas) * 100)),
        'framework_areas_covered': conversation.get('framework_areas_covered', [])
    }

def get_current_framework_area(conversation):
    """Get the current framework area to focus on"""
    areas_covered = conversation.get('framework_areas_covered', [])
    
    # Find the next area that hasn't been covered
    for area in FRAMEWORK_AREAS:
        if area['name'] not in areas_covered:
            return area
    
    # If all areas covered, return the last area for final questions
    return FRAMEWORK_AREAS[-1]

def should_advance_to_next_area(message, current_area):
    """Determine if we should move to the next framework area"""
    
    # Simple heuristic: if message is substantial (>20 words) and addresses the area
    if len(message.split()) > 20:
        return True
    
    # Check if user explicitly indicates they want to move on
    move_on_phrases = ['next', 'move on', 'continue', 'done with', 'finished']
    message_lower = message.lower()
    
    return any(phrase in message_lower for phrase in move_on_phrases)

def create_recovery_conversation(session_id, user_message):
    """Create a new conversation when session is lost, with context recovery"""
    
    conversation = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'framework_areas_covered': [],
        'current_area_index': 0,
        'recovered_session': True
    }
    
    conversations[session_id] = conversation
    
    # Add user message that triggered recovery
    user_msg = {
        "id": str(uuid.uuid4()),
        "sender": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    }
    conversation['messages'].append(user_msg)
    
    # Create recovery message
    recovery_message = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": "I see we got disconnected! No worries - let's continue building your AI course. Based on what you just shared, let me help you move forward with the She Is AI framework.\n\nLet's start fresh: Who are your learners? (students, professionals, career changers, etc.)",
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
    
    # Create new conversation
    conversation = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'framework_areas_covered': [],
        'current_area_index': 0
    }
    
    conversations[session_id] = conversation
    
    # Create welcome message
    welcome_message = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": "Hi! I'm the She Is AI Course Design Assistant. I'm here to help you create an incredible AI course using our proven educational framework.\n\nLet's start by understanding your learners better. Our framework emphasizes inclusive design from the very beginning.\n\nWho are your learners? (students, professionals, career changers, etc.)",
        "timestamp": datetime.now().isoformat(),
        "message_type": "welcome"
    }
    
    conversation['messages'].append(welcome_message)
    
    # Calculate initial progress
    progress = calculate_progress(conversation)
    
    return jsonify({
        "session_id": session_id,
        "welcome_message": welcome_message,
        "conversation": progress
    })

@app.route('/api/conversations/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message in an existing conversation - WITH BULLETPROOF SESSION RECOVERY"""
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # BULLETPROOF SESSION HANDLING
    if session_id not in conversations:
        print(f"Session {session_id} not found - creating recovery conversation")
        
        # Auto-recover by creating new conversation with context
        conversation, recovery_message = create_recovery_conversation(session_id, message)
        
        return jsonify({
            "ai_response": recovery_message,
            "safety_violation": False,
            "session_recovered": True,
            "conversation_update": calculate_progress(conversation)
        })
    
    conversation = conversations[session_id]
    
    # Add user message to conversation
    user_message = {
        "id": str(uuid.uuid4()),
        "sender": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    }
    
    conversation['messages'].append(user_message)
    
    # Check for safety violations
    if check_safety_violations(message):
        safety_response = get_safety_response()
        conversation['messages'].append(safety_response)
        
        return jsonify({
            "ai_response": safety_response,
            "safety_violation": True,
            "session_recovered": False,
            "conversation_update": calculate_progress(conversation)
        })
    
    # Get current framework area
    current_area = get_current_framework_area(conversation)
    
    # Check if we should advance to next area
    if should_advance_to_next_area(message, current_area):
        # Mark current area as covered
        if current_area['name'] not in conversation['framework_areas_covered']:
            conversation['framework_areas_covered'].append(current_area['name'])
        
        # Get next area
        current_area = get_current_framework_area(conversation)
    
    # Generate AI response
    progress = calculate_progress(conversation)
    ai_content = get_ai_response(message, conversation['messages'], current_area, progress)
    
    # Create AI response
    ai_response = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": ai_content,
        "timestamp": datetime.now().isoformat(),
        "message_type": "framework_guidance"
    }
    
    conversation['messages'].append(ai_response)
    
    # Update progress
    updated_progress = calculate_progress(conversation)
    
    return jsonify({
        "ai_response": ai_response,
        "safety_violation": False,
        "session_recovered": False,
        "conversation_update": updated_progress
    })

@app.route('/api/conversations/<session_id>/export', methods=['GET'])
def export_conversation(session_id):
    """Export conversation data - WITH SESSION RECOVERY"""
    
    if session_id not in conversations:
        return jsonify({
            "error": "Conversation not found",
            "session_id": session_id,
            "recovery_available": True
        }), 404
    
    conversation = conversations[session_id]
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify({
            "session_id": session_id,
            "conversation": conversation,
            "framework_progress": calculate_progress(conversation),
            "export_timestamp": datetime.now().isoformat()
        })
    
    elif format_type == 'csv':
        # Simple CSV export of messages
        csv_data = "Timestamp,Sender,Content\n"
        for msg in conversation['messages']:
            csv_data += f"{msg['timestamp']},{msg['sender']},\"{msg['content']}\"\n"
        
        return csv_data, 200, {'Content-Type': 'text/csv'}
    
    else:
        return jsonify({"error": "Unsupported format"}), 400

# BULLETPROOF ERROR HANDLING
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

