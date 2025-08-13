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

# She Is AI Framework Areas with completion criteria
FRAMEWORK_AREAS = [
    {
        "name": "Learner Understanding",
        "completion_criteria": ["learner_type", "experience_level", "goals"],
        "questions": [
            "Who are your learners? (students, professionals, career changers, etc.)",
            "What's their current level? (complete beginners, some tech background, etc.)",
            "What are their main goals? (career preparation, general education, specific skills, etc.)"
        ]
    },
    {
        "name": "AI in Context",
        "completion_criteria": ["ai_tools", "practical_applications", "relevance"],
        "questions": [
            "What specific AI tools or applications will you focus on?",
            "How will AI impact your learners' field or work?",
            "What practical examples will make AI concepts tangible?"
        ]
    },
    {
        "name": "Ethics & Responsible AI",
        "completion_criteria": ["ethical_considerations", "safety_measures"],
        "questions": [
            "What ethical considerations are most important for your learners?",
            "How will you ensure responsible AI use in your course?"
        ]
    },
    {
        "name": "Bias Recognition & Equity",
        "completion_criteria": ["bias_awareness", "inclusive_design"],
        "questions": [
            "How will you help learners recognize and prevent bias?",
            "What strategies ensure your course is inclusive and equitable?"
        ]
    },
    {
        "name": "Assessment Strategy",
        "completion_criteria": ["assessment_methods", "practical_evaluation"],
        "questions": [
            "How will you assess learning through hands-on projects?",
            "What will learners create to demonstrate their understanding?"
        ]
    }
]

def extract_course_info(messages):
    """Extract comprehensive course information from conversation"""
    course_info = {
        "learner_type": None,
        "experience_level": None,
        "goals": None,
        "subject_area": None,
        "ai_tools": [],
        "practical_applications": [],
        "assessment_methods": [],
        "ethical_considerations": [],
        "bias_awareness": False,
        "inclusive_design": False
    }
    
    for msg in messages:
        if msg.get('sender') == 'user':
            content = msg.get('content', '').lower()
            
            # Extract learner information
            if 'professional' in content:
                course_info["learner_type"] = "professionals"
            elif 'student' in content or 'high school' in content:
                course_info["learner_type"] = "students"
            elif 'career chang' in content:
                course_info["learner_type"] = "career changers"
            
            # Extract experience level
            if 'beginner' in content:
                course_info["experience_level"] = "beginners"
            elif 'intermediate' in content:
                course_info["experience_level"] = "intermediate"
            elif 'advanced' in content:
                course_info["experience_level"] = "advanced"
            
            # Extract AI tools
            if 'gamma' in content:
                course_info["ai_tools"].append("Gamma")
            if 'canva' in content:
                course_info["ai_tools"].append("Canva")
            if 'powerpoint' in content or 'presentation' in content:
                course_info["subject_area"] = "presentations"
            
            # Extract goals and applications
            if 'faster' in content or 'efficiently' in content or 'save time' in content:
                course_info["goals"] = "efficiency and time-saving"
            if 'visual' in content or 'image' in content:
                course_info["practical_applications"].append("visual content creation")
            
            # Extract assessment methods
            if 'hands-on' in content or 'doing' in content or 'presenting' in content:
                course_info["assessment_methods"].append("hands-on projects")
            if 'feedback' in content or 'survey' in content:
                course_info["assessment_methods"].append("feedback and surveys")
    
    return course_info

def detect_bias_or_exclusion(message):
    """Detect potential bias or exclusionary language"""
    message_lower = message.lower()
    
    # Exclusionary language patterns
    exclusionary_patterns = [
        "only teach", "don't teach", "can't come to", "not for", "exclude",
        "not suitable for", "only for", "not allowed", "restricted to"
    ]
    
    # Bias indicators
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

def get_bias_correction_response(bias_info, message):
    """Generate appropriate bias correction response"""
    if bias_info["has_exclusionary_language"]:
        return "I notice some language that might exclude certain learners. The She Is AI framework emphasizes inclusive, bias-free education that welcomes all learners regardless of background. How can we redesign your approach to be more inclusive and accessible to diverse learners?"
    
    elif bias_info["has_bias_indicators"]:
        return "That approach might unintentionally create barriers for some learners. Our framework focuses on inclusive design that assumes all learners can succeed with proper support. How might you adjust your course to be more welcoming and supportive for diverse learning styles and backgrounds?"
    
    return None

def check_area_completion(area, course_info):
    """Check if a framework area has sufficient information"""
    if area["name"] == "Learner Understanding":
        return (course_info["learner_type"] and 
                course_info["experience_level"] and 
                (course_info["goals"] or course_info["subject_area"]))
    
    elif area["name"] == "AI in Context":
        return (len(course_info["ai_tools"]) > 0 and 
                len(course_info["practical_applications"]) > 0 and
                course_info["subject_area"])
    
    elif area["name"] == "Assessment Strategy":
        return len(course_info["assessment_methods"]) > 0
    
    # For other areas, check if user has provided substantial responses
    return False

def get_completion_celebration(area_name, course_info):
    """Generate positive reinforcement for completed areas"""
    celebrations = {
        "Learner Understanding": f"Excellent! You've clearly identified your target learners: {course_info['learner_type']} at {course_info['experience_level']} level. This foundation is perfect for the She Is AI framework.",
        
        "AI in Context": f"Outstanding! Your focus on {', '.join(course_info['ai_tools'])} for {course_info['subject_area']} with {', '.join(course_info['practical_applications'])} is exactly the kind of practical, relevant approach our framework promotes.",
        
        "Assessment Strategy": f"Perfect! Your hands-on assessment approach with {', '.join(course_info['assessment_methods'])} aligns beautifully with our portfolio-based evaluation principles."
    }
    
    return celebrations.get(area_name, f"Great work on the {area_name} area! Your approach aligns well with our framework.")

def should_end_conversation(course_info, areas_covered):
    """Determine if conversation should end with summary"""
    # End if we have core information across multiple areas
    has_learners = course_info["learner_type"] and course_info["experience_level"]
    has_ai_context = len(course_info["ai_tools"]) > 0 and course_info["subject_area"]
    has_assessment = len(course_info["assessment_methods"]) > 0
    
    return has_learners and has_ai_context and has_assessment

def generate_course_summary(course_info):
    """Generate comprehensive course summary and validation"""
    summary = f"""🎉 **Congratulations! You've designed an excellent AI course!**

## **Your Course Design Summary:**

**Target Learners:** {course_info['learner_type'].title()} at {course_info['experience_level']} level
**Subject Focus:** {course_info['subject_area'].title()} using AI tools
**AI Tools:** {', '.join(course_info['ai_tools'])}
**Key Applications:** {', '.join(course_info['practical_applications'])}
**Assessment Methods:** {', '.join(course_info['assessment_methods'])}

## **Framework Alignment:**
✅ **Learner-Centered Design** - You've clearly identified your audience and their needs
✅ **Practical AI Applications** - Your tool selection is relevant and hands-on
✅ **Inclusive Approach** - Your design welcomes diverse learners
✅ **Authentic Assessment** - Your evaluation methods are practical and meaningful

## **Why This Course Will Succeed:**
Your course design perfectly embodies the She Is AI principles of inclusive, practical, and engaging AI education. You've created a learning experience that will genuinely prepare your learners for AI-enhanced work.

## **Next Steps:**
🔄 **Export Your Course Design** - Use the Export button to save your course plan in multiple formats
📊 **Download Summary** - Get a detailed course outline you can use for implementation
📋 **Share Your Vision** - Your course design is ready to share with stakeholders

**Your course is ready to launch! Well done!**"""

    return summary

def get_ai_response(message, conversation):
    """Generate intelligent AI response with bias detection and natural flow"""
    
    messages = conversation.get('messages', [])
    course_info = extract_course_info(messages)
    areas_covered = conversation.get('framework_areas_covered', [])
    
    # Check for bias or exclusionary language
    bias_info = detect_bias_or_exclusion(message)
    if bias_info["severity"] != "none":
        bias_response = get_bias_correction_response(bias_info, message)
        if bias_response:
            return bias_response
    
    # Check if conversation should end with summary
    if should_end_conversation(course_info, areas_covered):
        return generate_course_summary(course_info)
    
    # Find current area to work on
    current_area = None
    for area in FRAMEWORK_AREAS:
        if area["name"] not in areas_covered:
            # Check if this area is complete
            if check_area_completion(area, course_info):
                # Celebrate completion and mark as covered
                celebration = get_completion_celebration(area["name"], course_info)
                conversation['framework_areas_covered'].append(area["name"])
                
                # Find next area
                next_area = None
                for next_a in FRAMEWORK_AREAS:
                    if next_a["name"] not in conversation['framework_areas_covered']:
                        next_area = next_a
                        break
                
                if next_area:
                    return f"{celebration}\n\nNow let's move to {next_area['name']}. {next_area['questions'][0]}"
                else:
                    return generate_course_summary(course_info)
            else:
                current_area = area
                break
    
    if not current_area:
        return generate_course_summary(course_info)
    
    # Build conversation context
    conversation_history = []
    for msg in messages[-4:]:
        if msg.get('sender') == 'user':
            conversation_history.append(f"User: {msg.get('content')}")
        elif msg.get('sender') == 'assistant':
            conversation_history.append(f"Assistant: {msg.get('content')}")
    
    # Create context-aware system prompt
    system_prompt = f"""You are a professional She Is AI Course Design Consultant. You help educators create inclusive, bias-free AI courses.

COURSE INFORMATION GATHERED:
- Learners: {course_info.get('learner_type', 'Not specified')} ({course_info.get('experience_level', 'level not specified')})
- Subject: {course_info.get('subject_area', 'Not specified')}
- AI Tools: {', '.join(course_info.get('ai_tools', []))}
- Applications: {', '.join(course_info.get('practical_applications', []))}

CURRENT FRAMEWORK AREA: {current_area['name']}
AREAS COMPLETED: {', '.join(areas_covered)}

CONVERSATION HISTORY:
{chr(10).join(conversation_history)}

INSTRUCTIONS:
1. Be encouraging and positive about their progress
2. Ask ONE focused question to advance the current area
3. Keep responses concise (2-3 sentences max)
4. Build on information already provided
5. Never repeat questions about information you already know
6. If they've provided good information for the current area, celebrate it and move forward
7. Focus on practical, actionable course design advice

Current area focus: {current_area['name']}
Next question to explore: {current_area['questions'][0]}

Provide a helpful response that moves the conversation forward naturally."""

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
        
        # Fallback responses based on current area
        if current_area['name'] == "Ethics & Responsible AI":
            return f"Great progress so far! For the {current_area['name']} area: {current_area['questions'][0]}"
        elif current_area['name'] == "Bias Recognition & Equity":
            return f"Excellent work! Now for {current_area['name']}: {current_area['questions'][0]}"
        else:
            return f"You're doing great! Let's explore {current_area['name']}: {current_area['questions'][0]}"

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
    """Calculate progress through framework areas"""
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
    recovery_content = "Welcome back! I'm here to help you create an amazing AI course using the She Is AI framework. "
    
    if 'professional' in user_message.lower():
        recovery_content += "I can see you're working on a course for professionals. Let's build something incredible together! What specific AI skills or tools do you want them to learn?"
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
    """Send a message with professional consultation experience"""
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
    
    # Generate AI response with professional consultation approach
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
    """Export conversation data with course summary"""
    if session_id not in conversations:
        return jsonify({
            "error": "Conversation not found",
            "session_id": session_id,
            "recovery_available": True
        }), 404
    
    conversation = conversations[session_id]
    course_info = extract_learner_info(conversation.get('messages', []))
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify({
            "session_id": session_id,
            "conversation": conversation,
            "course_summary": course_info,
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

