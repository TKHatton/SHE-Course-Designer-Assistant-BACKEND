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
        "key_info": ["learner_type", "experience_level", "goals"],
        "questions": [
            "Who are your learners? (students, professionals, career changers, etc.)",
            "What's their current level? (complete beginners, some tech background, etc.)",
            "What are their main goals? (career preparation, general education, specific skills, etc.)"
        ]
    },
    {
        "name": "AI in Context",
        "key_info": ["ai_applications", "field_relevance", "practical_examples"],
        "questions": [
            "How will AI shape your learners' field/topic? (tools, workflows, industry examples)",
            "What specific AI applications are most relevant to your subject area?",
            "How can you make AI concepts tangible and relatable to your learners?"
        ]
    },
    {
        "name": "Ethics & Responsible AI Use",
        "key_info": ["ethical_considerations", "safety_measures", "real_world_examples"],
        "questions": [
            "What ethical considerations are most important for your learners to understand?",
            "How will you help them design safe, fair, and trustworthy AI experiences?",
            "What real-world examples of AI ethics can you incorporate?"
        ]
    },
    {
        "name": "Bias Recognition & Equity",
        "key_info": ["bias_detection", "equity_strategies", "inclusive_design"],
        "questions": [
            "How will you help learners spot bias in AI systems?",
            "What strategies will you teach for designing equitable AI systems?",
            "How will you address bias in your own course design and delivery?"
        ]
    },
    {
        "name": "AI Skills for the Future",
        "key_info": ["career_skills", "job_opportunities", "hands_on_projects"],
        "questions": [
            "What specific AI-related skills will your learners develop for career readiness?",
            "How will you connect these skills to real job opportunities?",
            "What hands-on projects will demonstrate these skills?"
        ]
    },
    {
        "name": "Assessment Strategy",
        "key_info": ["assessment_methods", "portfolio_items", "evaluation_criteria"],
        "questions": [
            "How will you assess learning through authentic, portfolio-based evaluation?",
            "What real-world applications will learners create to demonstrate knowledge?",
            "How will peer evaluation and collaborative assessment be integrated?"
        ]
    }
]

def extract_learner_info(messages):
    """Extract key information about learners from conversation history"""
    learner_info = {
        "type": None,
        "level": None,
        "goals": None,
        "subject_area": None
    }
    
    # Look through messages for learner information
    for msg in messages:
        if msg.get('sender') == 'user':
            content = msg.get('content', '').lower()
            
            # Extract learner type
            if 'professional' in content:
                learner_info["type"] = "professionals"
            elif 'student' in content:
                learner_info["type"] = "students"
            elif 'career chang' in content:
                learner_info["type"] = "career changers"
            
            # Extract level
            if 'beginner' in content:
                learner_info["level"] = "beginners"
            elif 'intermediate' in content:
                learner_info["level"] = "intermediate"
            elif 'advanced' in content:
                learner_info["level"] = "advanced"
            elif 'can make great' in content or 'experienced' in content:
                learner_info["level"] = "experienced"
            
            # Extract subject area/goals
            if 'powerpoint' in content or 'presentation' in content:
                learner_info["subject_area"] = "PowerPoint/presentations"
                learner_info["goals"] = "create presentations faster and more efficiently"
            elif 'quickly' in content and 'efficiently' in content:
                learner_info["goals"] = "work more efficiently"
    
    return learner_info

def get_current_framework_area(conversation):
    """Get the current framework area based on what's been covered"""
    learner_info = extract_learner_info(conversation.get('messages', []))
    areas_covered = conversation.get('framework_areas_covered', [])
    
    # If we have basic learner info, move to next areas
    if learner_info["type"] and learner_info["level"]:
        # Mark learner understanding as covered if we have the info
        if "Learner Understanding" not in areas_covered:
            conversation['framework_areas_covered'].append("Learner Understanding")
            areas_covered = conversation['framework_areas_covered']
    
    # Find the next area that hasn't been covered
    for area in FRAMEWORK_AREAS:
        if area['name'] not in areas_covered:
            return area
    
    # If all areas covered, return the last area
    return FRAMEWORK_AREAS[-1]

def get_ai_response(message, conversation):
    """Generate AI response with proper conversation memory"""
    
    messages = conversation.get('messages', [])
    learner_info = extract_learner_info(messages)
    current_area = get_current_framework_area(conversation)
    
    # Build conversation history for AI
    conversation_history = []
    for msg in messages[-6:]:  # Last 6 messages for context
        if msg.get('sender') == 'user':
            conversation_history.append(f"User: {msg.get('content')}")
        elif msg.get('sender') == 'assistant':
            conversation_history.append(f"Assistant: {msg.get('content')}")
    
    # Create context-aware system prompt
    system_prompt = f"""You are the She Is AI Course Design Assistant. You help educators create AI courses using our framework.

LEARNER INFORMATION DISCOVERED:
- Type: {learner_info.get('type', 'Not specified')}
- Level: {learner_info.get('level', 'Not specified')}
- Subject Area: {learner_info.get('subject_area', 'Not specified')}
- Goals: {learner_info.get('goals', 'Not specified')}

CURRENT FRAMEWORK AREA: {current_area['name']}

CONVERSATION HISTORY:
{chr(10).join(conversation_history)}

INSTRUCTIONS:
1. NEVER repeat questions about information you already know
2. If learner info is complete, move to the next framework area
3. Keep responses concise (2-3 sentences max)
4. Ask ONE specific question to advance the conversation
5. Build on what the user has already shared

CURRENT AREA FOCUS: {current_area['name']}
Key questions for this area: {current_area['questions']}

Based on the conversation history and current area, provide a helpful response that moves the conversation forward WITHOUT repeating information you already know."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"OpenAI API error: {e}")
        
        # Fallback response based on current area and learner info
        if current_area['name'] == "Learner Understanding" and learner_info.get('type'):
            return f"Perfect! So you're teaching {learner_info['type']} who are {learner_info.get('level', 'experienced')} with {learner_info.get('subject_area', 'presentations')}. Now let's explore how AI will specifically impact their work. What AI tools or workflows do you think would be most relevant for creating presentations efficiently?"
        elif current_area['name'] == "AI in Context":
            return "Great! Now let's think about the specific AI applications. For PowerPoint creation, what AI tools do you think would be most valuable - content generation, design assistance, or automation workflows?"
        else:
            return f"Let's continue with {current_area['name']}. {current_area['questions'][0]}"

def check_safety_violations(message):
    """Check for inappropriate content or off-topic requests"""
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
    """Calculate progress through the framework areas"""
    areas_covered = len(conversation.get('framework_areas_covered', []))
    total_areas = len(FRAMEWORK_AREAS)
    
    return {
        'current_step': areas_covered + 1,
        'total_steps': total_areas,
        'completion_percentage': min(100, int((areas_covered / total_areas) * 100)),
        'framework_areas_covered': conversation.get('framework_areas_covered', [])
    }

def create_recovery_conversation(session_id, user_message):
    """Create a new conversation when session is lost"""
    conversation = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'framework_areas_covered': [],
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
    
    # Create contextual recovery message
    recovery_content = "I see we got disconnected! No worries - let's continue building your AI course. "
    
    # Try to extract context from the user message
    if 'professional' in user_message.lower():
        recovery_content += "I can see you're working on a course for professionals. Let's continue from where we left off. What specific AI skills or tools do you want them to learn?"
    else:
        recovery_content += "Based on what you just shared, let me help you move forward with the She Is AI framework. Can you tell me more about your target learners?"
    
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
        'messages': [],
        'framework_areas_covered': []
    }
    
    conversations[session_id] = conversation
    
    welcome_message = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": "Hi! I'm the She Is AI Course Design Assistant. I'm here to help you create an incredible AI course using our proven educational framework.\n\nLet's start by understanding your learners better. Our framework emphasizes inclusive design from the very beginning.\n\nWho are your learners? (students, professionals, career changers, etc.)",
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
    """Send a message with proper memory and context tracking"""
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
    
    # Generate AI response with full conversation context
    ai_content = get_ai_response(message, conversation)
    
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
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify({
            "session_id": session_id,
            "conversation": conversation,
            "learner_info": extract_learner_info(conversation.get('messages', [])),
            "framework_progress": calculate_progress(conversation),
            "export_timestamp": datetime.now().isoformat()
        })
    
    elif format_type == 'csv':
        csv_data = "Timestamp,Sender,Content\n"
        for msg in conversation['messages']:
            csv_data += f"{msg['timestamp']},{msg['sender']},\"{msg['content']}\"\n"
        
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

