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

def extract_comprehensive_course_info(messages):
    """Extract all course information from conversation"""
    info = {
        "learner_type": None,
        "experience_level": None,
        "background": None,
        "goals": [],
        "ai_tools": [],
        "core_concepts": [],
        "teaching_methods": [],
        "assessment_approach": [],
        "subject_area": None,
        "course_structure": None,
        "response_count": 0
    }
    
    for msg in messages:
        if msg.get('sender') == 'user':
            content = msg.get('content', '').lower()
            info["response_count"] += 1
            
            # Learner type
            if 'career chang' in content:
                info["learner_type"] = "career changers"
            elif 'professional' in content:
                info["learner_type"] = "professionals"
            elif 'student' in content:
                info["learner_type"] = "students"
            
            # Experience level
            if 'beginner' in content or 'new to' in content or 'basic' in content:
                info["experience_level"] = "beginners"
            elif 'intermediate' in content:
                info["experience_level"] = "intermediate"
            elif 'data entry' in content:
                info["background"] = "data entry workers"
            
            # Goals
            if 'three new skills' in content or 'hands on experience' in content:
                info["goals"].append("practical skill development")
            if 'see how it can change their lives' in content:
                info["goals"].append("personal transformation")
            if 'options' in content and 'different' in content:
                info["goals"].append("career exploration")
            
            # AI Tools
            if 'gemini' in content:
                info["ai_tools"].append("Gemini")
            if 'notebook' in content or 'notebooklm' in content:
                info["ai_tools"].append("NotebookLM")
            if 'real time' in content or 'streaming' in content:
                info["ai_tools"].append("Google real-time streaming")
            if 'chat gpt' in content or 'chatgpt' in content:
                info["ai_tools"].append("ChatGPT")
            
            # Core concepts
            if 'faster' in content and 'ai' in content:
                info["core_concepts"].append("AI efficiency")
            if 'trust' in content and 'not' in content:
                info["core_concepts"].append("critical evaluation")
            if 'tokens' in content:
                info["core_concepts"].append("how AI works")
            if 'humanize' in content and 'not' in content:
                info["core_concepts"].append("proper AI relationship")
            if 'practice' in content or 'dig further' in content:
                info["core_concepts"].append("persistence and iteration")
            
            # Teaching methods
            if 'slow' in content or 'checkpoints' in content:
                info["teaching_methods"].append("paced learning with checkpoints")
            if 'body language' in content or 'circulate' in content:
                info["teaching_methods"].append("attentive monitoring")
            if 'examples' in content and 'before' in content:
                info["teaching_methods"].append("demonstration before practice")
            if 'positive feedback' in content:
                info["teaching_methods"].append("supportive feedback")
    
    return info

def calculate_completion_score(course_info):
    """Calculate how complete the course design is"""
    score = 0
    
    # Core requirements (20 points each)
    if course_info["learner_type"]: score += 20
    if course_info["ai_tools"]: score += 20
    if course_info["goals"]: score += 20
    if course_info["core_concepts"]: score += 20
    if course_info["teaching_methods"]: score += 20
    
    return min(100, score)

def should_conclude_conversation(course_info):
    """Determine if conversation should end with summary"""
    # End if we have substantial information across key areas
    has_learners = course_info["learner_type"] and (course_info["experience_level"] or course_info["background"])
    has_tools = len(course_info["ai_tools"]) >= 2
    has_goals = len(course_info["goals"]) >= 1
    has_concepts = len(course_info["core_concepts"]) >= 2
    has_methods = len(course_info["teaching_methods"]) >= 2
    
    # Also end if user has given 4+ substantial responses
    enough_responses = course_info["response_count"] >= 4
    
    return (has_learners and has_tools and has_goals and has_concepts) or enough_responses

def generate_final_course_summary(course_info):
    """Generate comprehensive final course summary"""
    
    # Build dynamic summary based on what was provided
    learner_desc = f"{course_info['learner_type']}"
    if course_info["background"]:
        learner_desc += f" (specifically {course_info['background']})"
    if course_info["experience_level"]:
        learner_desc += f" at {course_info['experience_level']} level"
    
    tools_list = ", ".join(course_info["ai_tools"]) if course_info["ai_tools"] else "Various AI tools"
    goals_list = ", ".join(course_info["goals"]) if course_info["goals"] else "Skill development and career growth"
    concepts_list = ", ".join(course_info["core_concepts"]) if course_info["core_concepts"] else "Practical AI understanding"
    methods_list = ", ".join(course_info["teaching_methods"]) if course_info["teaching_methods"] else "Supportive, hands-on approach"
    
    summary = f"""🎉 **Congratulations! You've designed an excellent AI course!**

## **Your Course Design Summary:**

**🎯 Target Learners:** {learner_desc.title()}
**🛠️ AI Tools:** {tools_list}
**📈 Learning Goals:** {goals_list.title()}
**🧠 Core Concepts:** {concepts_list.title()}
**👩‍🏫 Teaching Approach:** {methods_list.title()}

## **🌟 Why This Course Will Succeed:**

Your course design perfectly embodies the She Is AI principles:
✅ **Learner-Centered** - You've clearly identified your audience and their unique needs
✅ **Practical & Relevant** - Your tool selection directly addresses real-world applications
✅ **Inclusive & Supportive** - Your teaching methods ensure no one gets left behind
✅ **Empowering** - You're giving learners agency to explore and find their own path

## **🚀 Framework Alignment:**

Your approach aligns beautifully with our core framework areas:
- **Learner Understanding** ✅ Complete
- **AI in Context** ✅ Complete  
- **Practical Application** ✅ Complete
- **Supportive Pedagogy** ✅ Complete

## **📋 Next Steps:**

🔄 **Export Your Course Design** - Click the Export button to download your complete course plan
📊 **Get Detailed Outline** - Choose JSON format for a structured course blueprint
📝 **Share Your Vision** - Your course design is ready to present to stakeholders
🎯 **Start Implementation** - You have everything needed to launch this course

**Your course will genuinely transform lives and careers. Well done!**

*Ready to export? Use the Export button above to save your course design in multiple formats!*"""

    return summary

def detect_user_frustration_or_completion_signals(message):
    """Detect when user is signaling the conversation should end"""
    message_lower = message.lower()
    
    completion_signals = [
        "wrap it up", "wrap this up", "end this", "conclude", "summary",
        "that's enough", "we're done", "finish this", "close this out",
        "already gave", "already said", "already told", "already covered",
        "going in circles", "looping", "repeating", "asked this already",
        "time to stop", "needs to end", "should end", "wrap up"
    ]
    
    frustration_signals = [
        "frustrated", "annoying", "waste of time", "not working",
        "stuck", "broken", "terrible", "awful", "horrible"
    ]
    
    has_completion = any(signal in message_lower for signal in completion_signals)
    has_frustration = any(signal in message_lower for signal in frustration_signals)
    
    return {
        "should_conclude": has_completion,
        "user_frustrated": has_frustration,
        "immediate_end": has_completion or has_frustration
    }

def detect_bias_or_exclusion(message):
    """Detect potential bias or exclusionary language"""
    message_lower = message.lower()
    
    exclusionary_patterns = [
        "only teach", "don't teach", "can't come to", "not for", "exclude",
        "not suitable for", "only for", "not allowed", "restricted to"
    ]
    
    bias_patterns = [
        "too difficult for", "not smart enough", "can't handle", "not capable",
        "not ready for", "too advanced for", "not suited for"
    ]
    
    exclusionary_detected = any(pattern in message_lower for pattern in exclusionary_patterns)
    bias_detected = any(pattern in message_lower for pattern in bias_patterns)
    
    return {
        "has_exclusionary_language": exclusionary_detected,
        "has_bias_indicators": bias_detected,
        "severity": "high" if exclusionary_detected else "medium" if bias_detected else "none"
    }

def get_bias_correction_response(bias_info):
    """Generate appropriate bias correction response"""
    if bias_info["has_exclusionary_language"]:
        return "I notice some language that might exclude certain learners. The She Is AI framework emphasizes inclusive, bias-free education that welcomes all learners regardless of background. How can we redesign your approach to be more inclusive and accessible to diverse learners?"
    
    elif bias_info["has_bias_indicators"]:
        return "That approach might unintentionally create barriers for some learners. Our framework focuses on inclusive design that assumes all learners can succeed with proper support. How might you adjust your course to be more welcoming and supportive for diverse learning styles and backgrounds?"
    
    return None

def get_intelligent_response(message, conversation):
    """Generate intelligent response with proper completion detection"""
    
    messages = conversation.get('messages', [])
    course_info = extract_comprehensive_course_info(messages)
    
    # Check for user completion signals first
    user_signals = detect_user_frustration_or_completion_signals(message)
    if user_signals["immediate_end"]:
        return generate_final_course_summary(course_info)
    
    # Check for bias/exclusion
    bias_info = detect_bias_or_exclusion(message)
    if bias_info["severity"] != "none":
        bias_response = get_bias_correction_response(bias_info)
        if bias_response:
            return bias_response
    
    # Check if we should naturally conclude
    if should_conclude_conversation(course_info):
        return generate_final_course_summary(course_info)
    
    # If we don't have enough info yet, ask one focused question
    if not course_info["learner_type"]:
        return "Who are your learners? (students, professionals, career changers, etc.)"
    
    elif not course_info["ai_tools"]:
        return f"Great! {course_info['learner_type'].title()} bring valuable experience. What specific AI tools would you like to focus on in your course?"
    
    elif not course_info["goals"]:
        return f"Excellent tool choices! What are the main outcomes you want your {course_info['learner_type']} to achieve by the end of the course?"
    
    elif len(course_info["core_concepts"]) < 2:
        return "What key AI concepts do you think are most important for your learners to understand?"
    
    else:
        # We have enough - conclude
        return generate_final_course_summary(course_info)

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

def calculate_accurate_progress(conversation):
    """Calculate accurate progress based on actual completion"""
    messages = conversation.get('messages', [])
    course_info = extract_comprehensive_course_info(messages)
    completion_score = calculate_completion_score(course_info)
    
    # Calculate steps based on what's actually been covered
    steps_completed = 0
    if course_info["learner_type"]: steps_completed += 1
    if course_info["ai_tools"]: steps_completed += 1  
    if course_info["goals"]: steps_completed += 1
    if course_info["core_concepts"]: steps_completed += 1
    if course_info["teaching_methods"]: steps_completed += 1
    
    return {
        'current_step': min(steps_completed, 5),
        'total_steps': 5,
        'completion_percentage': completion_score,
        'framework_areas_covered': [
            "Learner Understanding" if course_info["learner_type"] else None,
            "AI Tools & Context" if course_info["ai_tools"] else None,
            "Learning Goals" if course_info["goals"] else None,
            "Core Concepts" if course_info["core_concepts"] else None,
            "Teaching Methods" if course_info["teaching_methods"] else None
        ]
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
    
    # Create contextual recovery message
    recovery_content = "Welcome back! I'm here to help you create an amazing AI course using the She Is AI framework. "
    
    if 'professional' in user_message.lower():
        recovery_content += "I can see you're working on a course for professionals. Let's build something incredible together!"
    else:
        recovery_content += "Let's start by understanding your learners. Who are you designing this course for?"
    
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
    
    welcome_message = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": "Hi! I'm the She Is AI Course Design Assistant. I'm here to help you create an incredible AI course using our proven educational framework.\n\nLet's start by understanding your learners better. Our framework emphasizes inclusive design from the very beginning.\n\nWho are your learners? (students, professionals, career changers, etc.)",
        "timestamp": datetime.now().isoformat(),
        "message_type": "welcome"
    }
    
    conversation['messages'].append(welcome_message)
    progress = calculate_accurate_progress(conversation)
    
    return jsonify({
        "session_id": session_id,
        "welcome_message": welcome_message,
        "conversation": progress
    })

@app.route('/api/conversations/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message with intelligent completion detection"""
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
            "conversation_update": calculate_accurate_progress(conversation)
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
            "conversation_update": calculate_accurate_progress(conversation)
        })
    
    # Generate intelligent response
    ai_content = get_intelligent_response(message, conversation)
    
    ai_response = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": ai_content,
        "timestamp": datetime.now().isoformat(),
        "message_type": "framework_guidance"
    }
    
    conversation['messages'].append(ai_response)
    updated_progress = calculate_accurate_progress(conversation)
    
    return jsonify({
        "ai_response": ai_response,
        "safety_violation": False,
        "session_recovered": False,
        "conversation_update": updated_progress
    })

@app.route('/api/conversations/<session_id>/export', methods=['GET'])
def export_conversation(session_id):
    """Export conversation data with comprehensive course summary"""
    if session_id not in conversations:
        return jsonify({
            "error": "Conversation not found",
            "session_id": session_id,
            "recovery_available": True
        }), 404
    
    conversation = conversations[session_id]
    course_info = extract_comprehensive_course_info(conversation.get('messages', []))
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify({
            "session_id": session_id,
            "conversation": conversation,
            "course_design": course_info,
            "framework_progress": calculate_accurate_progress(conversation),
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

