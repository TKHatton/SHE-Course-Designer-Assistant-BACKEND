from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime
import openai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import io

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

# She Is AI Framework Areas - Complete Set
FRAMEWORK_AREAS = [
    "Learner Understanding",
    "AI in Context", 
    "Ethics & Responsible AI Use",
    "Bias Recognition & Equity",
    "Women's Role in AI",
    "AI Skills for the Future",
    "Assessment Strategy",
    "Universal Lesson Structure",
    "Content Progression",
    "Course Implementation"
]

def extract_course_information(messages):
    """Extract comprehensive course information from conversation"""
    info = {
        "learner_type": None,
        "learner_background": None,
        "ai_tools": [],
        "course_subject": None,
        "learning_goals": [],
        "ethical_considerations": [],
        "bias_awareness": [],
        "women_in_ai": [],
        "future_skills": [],
        "assessment_methods": [],
        "lesson_structure": [],
        "content_progression": [],
        "implementation_plan": [],
        "teaching_methods": [],
        "unique_aspects": [],
        "areas_covered": set()
    }
    
    for msg in messages:
        if msg.get('sender') == 'user':
            content = msg.get('content', '').lower()
            
            # Extract learner information
            if 'professional' in content:
                info["learner_type"] = "professionals"
            elif 'student' in content:
                info["learner_type"] = "students"
            elif 'career chang' in content:
                info["learner_type"] = "career changers"
            
            # Extract AI tools
            tools = ['n8n', 'gamma', 'canva', 'chatgpt', 'gemini', 'manus', 'claude']
            for tool in tools:
                if tool in content and tool not in info["ai_tools"]:
                    info["ai_tools"].append(tool)
            
            # Extract goals and methods
            if 'foundation' in content or 'basic' in content:
                info["learning_goals"].append("foundational understanding")
            if 'hands-on' in content or 'practical' in content:
                info["learning_goals"].append("practical application")
            if 'quiz' in content or 'assessment' in content:
                info["assessment_methods"].append("interactive assessment")
            
            # Track unique aspects
            if len(content) > 50:  # Substantial responses
                info["unique_aspects"].append(content[:100] + "..." if len(content) > 100 else content)
    
    return info

def determine_next_area_to_explore(conversation):
    """Intelligently determine next framework area based on conversation flow"""
    messages = conversation.get('messages', [])
    course_info = extract_course_information(messages)
    covered_areas = conversation.get('areas_covered', set())
    
    # Natural progression based on what's been discussed
    if not course_info["learner_type"]:
        return "Learner Understanding"
    
    if course_info["learner_type"] and not course_info["ai_tools"]:
        return "AI in Context"
    
    if course_info["ai_tools"] and "Ethics & Responsible AI Use" not in covered_areas:
        return "Ethics & Responsible AI Use"
    
    if "Ethics & Responsible AI Use" in covered_areas and "Bias Recognition & Equity" not in covered_areas:
        return "Bias Recognition & Equity"
    
    if "Bias Recognition & Equity" in covered_areas and "Women's Role in AI" not in covered_areas:
        return "Women's Role in AI"
    
    if len(covered_areas) >= 5 and "Assessment Strategy" not in covered_areas:
        return "Assessment Strategy"
    
    if len(covered_areas) >= 6 and "AI Skills for the Future" not in covered_areas:
        return "AI Skills for the Future"
    
    # Continue with remaining areas
    for area in FRAMEWORK_AREAS:
        if area not in covered_areas:
            return area
    
    return None  # All areas covered

def generate_natural_question(area, course_info, conversation_context):
    """Generate natural, conversational questions that build on previous responses"""
    
    # Get last few messages for context
    messages = conversation_context.get('messages', [])
    recent_context = ""
    if messages:
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get('sender') == 'user':
                last_user_msg = msg.get('content', '')
                break
        if last_user_msg:
            recent_context = last_user_msg[:150]
    
    # Natural conversation starters based on area and context
    if area == "Learner Understanding":
        return "I'd love to understand who you're designing this course for. Who are your learners, and what's their background with AI or technology?"
    
    elif area == "AI in Context":
        learner_ref = f"your {course_info['learner_type']}" if course_info['learner_type'] else "your learners"
        return f"That's a great foundation! What specific AI tools or platforms do you want to focus on with {learner_ref}?"
    
    elif area == "Ethics & Responsible AI Use":
        if course_info["ai_tools"]:
            tools = ", ".join(course_info["ai_tools"])
            return f"Excellent choice with {tools}! As we think about responsible AI education, what ethical considerations do you think are most important for your learners to understand?"
        return "As we design this course, what ethical aspects of AI do you want to make sure your learners understand?"
    
    elif area == "Bias Recognition & Equity":
        return "That's such important thinking about AI ethics! Building on that, how do you plan to help your learners recognize and address bias in AI systems?"
    
    elif area == "Women's Role in AI":
        return "I love your focus on inclusive AI! How might you highlight women's contributions and leadership in AI throughout your course?"
    
    elif area == "Assessment Strategy":
        return "Your approach sounds really thoughtful! How are you planning to assess whether your learners are truly grasping these concepts?"
    
    elif area == "AI Skills for the Future":
        return "That assessment approach makes a lot of sense! What specific AI-related skills do you want your learners to develop for their future careers?"
    
    elif area == "Universal Lesson Structure":
        return "Those are valuable skills! How do you envision structuring your individual lessons or sessions?"
    
    elif area == "Content Progression":
        return "Great lesson structure! How will you sequence the content - what comes first, and how will you build complexity?"
    
    elif area == "Course Implementation":
        return "This course design is really coming together! What's your plan for actually implementing and delivering this course?"
    
    return f"Let's explore {area}. How does this area fit into your course vision?"

def should_offer_final_consultation(conversation):
    """Determine if we should offer final consultation before summary"""
    covered_areas = conversation.get('areas_covered', set())
    messages = conversation.get('messages', [])
    user_responses = [msg for msg in messages if msg.get('sender') == 'user']
    
    # Offer consultation after covering 8+ areas or 10+ user responses
    return len(covered_areas) >= 8 or len(user_responses) >= 10

def generate_consultation_offer():
    """Generate final consultation offer"""
    offers = [
        "This course design is really taking shape! Is there anything else about your course you'd like to share or explore?",
        "I'm impressed with your thoughtful approach! Do you have any questions about your course design, or would you like suggestions on any particular aspect?",
        "Your course sounds fantastic! Before we wrap up, is there anything else you'd like to discuss or any area where you'd like some additional guidance?",
        "This is going to be an amazing course! Any final thoughts you'd like to share, or questions about how to strengthen your design even further?"
    ]
    
    import random
    return random.choice(offers)

def create_personalized_pdf_report(course_info, session_id):
    """Create a comprehensive, personalized PDF report"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    # Custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=HexColor('#2E86AB'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#A23B72'),
        spaceBefore=20,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        leftIndent=20
    )
    
    story = []
    
    # Title
    story.append(Paragraph("🎉 Your She Is AI Course Design", title_style))
    story.append(Spacer(1, 20))
    
    # Personalized opening
    learner_type = course_info.get('learner_type', 'learners').title()
    tools = ', '.join(course_info.get('ai_tools', ['various AI tools']))
    
    opening = f"""
    <b>Congratulations!</b> You've created an exceptional AI course design that truly embodies the She Is AI framework principles. 
    Your thoughtful approach to teaching {learner_type} using {tools} demonstrates a deep understanding of inclusive, 
    practical AI education.
    """
    story.append(Paragraph(opening, body_style))
    story.append(Spacer(1, 20))
    
    # Course Overview
    story.append(Paragraph("📋 Your Course Overview", heading_style))
    
    if course_info.get('learner_type'):
        story.append(Paragraph(f"<b>Target Learners:</b> {course_info['learner_type'].title()}", body_style))
    
    if course_info.get('ai_tools'):
        story.append(Paragraph(f"<b>AI Tools & Platforms:</b> {', '.join(course_info['ai_tools']).title()}", body_style))
    
    if course_info.get('learning_goals'):
        goals = ', '.join(course_info['learning_goals'])
        story.append(Paragraph(f"<b>Learning Goals:</b> {goals.title()}", body_style))
    
    if course_info.get('assessment_methods'):
        methods = ', '.join(course_info['assessment_methods'])
        story.append(Paragraph(f"<b>Assessment Approach:</b> {methods.title()}", body_style))
    
    story.append(Spacer(1, 20))
    
    # Framework Alignment
    story.append(Paragraph("🌟 She Is AI Framework Alignment", heading_style))
    
    framework_points = [
        "✅ <b>Learner-Centered Design:</b> You've clearly identified your audience and their unique needs",
        "✅ <b>Practical AI Applications:</b> Your tool selection directly addresses real-world applications", 
        "✅ <b>Inclusive & Equitable:</b> Your approach welcomes diverse learners and addresses bias",
        "✅ <b>Ethics-First:</b> You've considered responsible AI use throughout your design",
        "✅ <b>Future-Ready Skills:</b> Your course prepares learners for evolving AI landscape",
        "✅ <b>Authentic Assessment:</b> Your evaluation methods are practical and meaningful"
    ]
    
    for point in framework_points:
        story.append(Paragraph(point, body_style))
    
    story.append(Spacer(1, 20))
    
    # Why This Course Will Succeed
    story.append(Paragraph("🚀 Why Your Course Will Transform Lives", heading_style))
    
    success_factors = f"""
    Your course design stands out because of your thoughtful integration of practical skills with ethical considerations. 
    By focusing on {tools} while maintaining awareness of bias and inclusion, you're creating an educational experience 
    that doesn't just teach tools—it empowers learners to be responsible AI practitioners.
    
    Your emphasis on {', '.join(course_info.get('learning_goals', ['comprehensive understanding']))} ensures that 
    learners won't just learn to use AI, but will understand how to use it thoughtfully and effectively.
    """
    story.append(Paragraph(success_factors, body_style))
    story.append(Spacer(1, 20))
    
    # Implementation Roadmap
    story.append(Paragraph("📈 Your Implementation Roadmap", heading_style))
    
    roadmap = [
        "<b>Phase 1:</b> Finalize curriculum details and learning materials",
        "<b>Phase 2:</b> Develop hands-on exercises and assessment rubrics", 
        "<b>Phase 3:</b> Create inclusive learning environment and bias-checking protocols",
        "<b>Phase 4:</b> Launch pilot program with feedback collection",
        "<b>Phase 5:</b> Iterate and scale based on learner outcomes"
    ]
    
    for phase in roadmap:
        story.append(Paragraph(phase, body_style))
    
    story.append(Spacer(1, 30))
    
    # Closing motivation
    story.append(Paragraph("💪 You're Ready to Make an Impact", heading_style))
    
    closing = f"""
    <b>Your course will genuinely transform careers and lives.</b> By combining practical AI skills with ethical awareness 
    and inclusive design, you're not just teaching technology—you're empowering people to shape the future of AI.
    
    The She Is AI framework recognizes educators like you who understand that great AI education goes beyond tools 
    to encompass responsibility, equity, and empowerment. Your {learner_type.lower()} are fortunate to have an 
    instructor who cares deeply about both technical excellence and human impact.
    
    <b>Go forth and transform the world, one learner at a time!</b>
    """
    story.append(Paragraph(closing, body_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer

def get_conversational_response(message, conversation):
    """Generate natural, conversational responses using OpenAI"""
    
    messages = conversation.get('messages', [])
    course_info = extract_course_information(messages)
    covered_areas = conversation.get('areas_covered', set())
    
    # Check if we should offer final consultation
    if should_offer_final_consultation(conversation) and not conversation.get('offered_consultation', False):
        conversation['offered_consultation'] = True
        return generate_consultation_offer()
    
    # Check if user is indicating they're done
    completion_signals = ['done', 'finished', 'ready', 'wrap up', 'summary', 'that\'s all', 'nothing else']
    if any(signal in message.lower() for signal in completion_signals):
        return "Perfect! Let me create your comprehensive course design report. You can download it using the Export button above - it will be a detailed PDF celebrating your amazing course design!"
    
    # Determine next area to explore
    next_area = determine_next_area_to_explore(conversation)
    
    if not next_area:
        return "What an incredible course you've designed! You can now download your personalized course design report using the Export button above."
    
    # Generate natural question for next area
    natural_question = generate_natural_question(next_area, course_info, conversation)
    
    # Mark area as covered
    if 'areas_covered' not in conversation:
        conversation['areas_covered'] = set()
    conversation['areas_covered'].add(next_area)
    
    return natural_question

def check_safety_violations(message):
    """Check for inappropriate content"""
    inappropriate_keywords = [
        'personal advice', 'relationship', 'medical', 'legal advice', 
        'politics', 'religion', 'inappropriate', 'harmful'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in inappropriate_keywords)

def detect_bias_or_exclusion(message):
    """Detect potential bias or exclusionary language"""
    message_lower = message.lower()
    
    exclusionary_patterns = [
        "only for", "not for", "can't handle", "too difficult for",
        "not smart enough", "exclude", "not suitable for"
    ]
    
    has_bias = any(pattern in message_lower for pattern in exclusionary_patterns)
    
    if has_bias:
        return "I notice some language that might exclude certain learners. The She Is AI framework emphasizes inclusive design that welcomes all learners. How can we make your course more accessible and inclusive?"
    
    return None

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
    """Calculate progress based on areas covered"""
    covered_areas = conversation.get('areas_covered', set())
    total_areas = len(FRAMEWORK_AREAS)
    
    return {
        'current_step': len(covered_areas),
        'total_steps': total_areas,
        'completion_percentage': min(100, int((len(covered_areas) / total_areas) * 100)),
        'framework_areas_covered': list(covered_areas)
    }

def create_recovery_conversation(session_id, user_message):
    """Create a new conversation when session is lost"""
    conversation = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'areas_covered': set(),
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
    
    # Create recovery message
    recovery_content = "Welcome back! I'm here to help you design an amazing AI course using the She Is AI framework. Let's continue building something incredible together! "
    
    # Get appropriate next question
    next_response = get_conversational_response(user_message, conversation)
    recovery_content += next_response
    
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
    """Initialize a new conversation with natural opening"""
    session_id = str(uuid.uuid4())
    
    conversation = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': [],
        'areas_covered': set()
    }
    
    conversations[session_id] = conversation
    
    welcome_message = {
        "id": str(uuid.uuid4()),
        "sender": "assistant",
        "content": "Hi! I'm your She Is AI Course Design Consultant. I'm excited to help you create an incredible AI course that's inclusive, practical, and transformative.\n\nI'll guide you through our comprehensive framework with natural conversation - no rigid surveys here! We'll explore about 10 key areas together, and I'll create a personalized course design report just for you.\n\nLet's start with the foundation: Who are you designing this course for, and what's their background with AI or technology?",
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
    """Send a message with sophisticated conversational flow"""
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
    
    # Generate conversational response
    ai_content = get_conversational_response(message, conversation)
    
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
    """Export personalized PDF report"""
    if session_id not in conversations:
        return jsonify({
            "error": "Conversation not found",
            "session_id": session_id
        }), 404
    
    conversation = conversations[session_id]
    course_info = extract_course_information(conversation.get('messages', []))
    
    # Create personalized PDF
    pdf_buffer = create_personalized_pdf_report(course_info, session_id)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'she_is_ai_course_design_{session_id[:8]}.pdf'
    )

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

