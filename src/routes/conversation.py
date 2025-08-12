from flask import Blueprint, request, jsonify
from src.models.conversation import db, Conversation, Message, FrameworkConcept
from src.utils.conversation_intelligence_simple import AdvancedConversationIntelligence
import uuid
import json
from datetime import datetime, timedelta
import time

conversation_bp = Blueprint('conversation', __name__)

# Initialize enhanced conversation intelligence
conv_intelligence = AdvancedConversationIntelligence()

# Rate limiting storage (in production, use Redis or similar)
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

@conversation_bp.route('/conversations', methods=['POST'])
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

@conversation_bp.route('/conversations/<session_id>', methods=['GET'])
def get_conversation(session_id):
    """Get conversation details and message history"""
    conversation = Conversation.query.filter_by(session_id=session_id).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    
    return jsonify({
        'conversation': conversation.to_dict(),
        'messages': [msg.to_dict() for msg in messages]
    })

@conversation_bp.route('/conversations/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message and get AI response with comprehensive safety measures"""
    
    # Rate limiting check
    if not check_rate_limit(session_id):
        return jsonify({
            'error': 'Rate limit exceeded. Please wait a few minutes before sending more messages.',
            'safety_notice': 'This limit helps ensure quality conversations and system security.'
        }), 429
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Enhanced input sanitization
    original_message = user_message
    user_message = conv_intelligence.sanitize_input(user_message)
    
    if not user_message:
        return jsonify({
            'error': 'Invalid message content',
            'safety_notice': 'Your message contained content that cannot be processed for security reasons.'
        }), 400
    
    # Check for safety violations
    safety_violations = conv_intelligence.detect_safety_violations(original_message)
    
    conversation = Conversation.query.filter_by(session_id=session_id).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    # If safety violations detected, respond with safety message
    if safety_violations:
        safety_response = conv_intelligence.generate_safety_response(safety_violations)
        
        # Log safety violation (in production, send to monitoring system)
        safety_msg = Message(
            conversation_id=conversation.id,
            sender='assistant',
            content=safety_response,
            message_type='safety_response'
        )
        db.session.add(safety_msg)
        db.session.commit()
        
        return jsonify({
            'ai_response': safety_msg.to_dict(),
            'safety_violation': True,
            'violation_types': safety_violations,
            'privacy_notice': 'Your responses help design your course and aren\'t stored permanently or shared'
        })
    
    # Get conversation history for analysis
    conversation_history = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    history_data = [{'sender': msg.sender, 'content': msg.content} for msg in conversation_history]
    
    # Enhanced analysis with boundary detection
    analysis = conv_intelligence.analyze_user_message(user_message, history_data)
    
    # Save user message with enhanced metadata
    user_msg = Message(
        conversation_id=conversation.id,
        sender='user',
        content=user_message,
        intent=analysis['intent'],
        confidence=analysis['confidence']
    )
    user_msg.set_framework_references(analysis['framework_references'])
    db.session.add(user_msg)
    
    # Generate intelligent AI response
    ai_response = conv_intelligence.generate_intelligent_response(user_message, conversation, analysis)
    
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
    
    # Update conversation progress (only advance if not a boundary violation or vague response)
    if not analysis.get('boundary_violation') and not analysis.get('is_vague'):
        conversation.current_step = min(conversation.current_step + 1, conversation.total_steps)
    
    conversation.completion_percentage = (conversation.current_step / conversation.total_steps) * 100
    conversation.updated_at = datetime.utcnow()
    
    # Update framework areas covered
    current_areas = conversation.get_framework_areas_covered()
    new_areas = list(set(current_areas + analysis['framework_references']))
    conversation.set_framework_areas_covered(new_areas)
    
    # Extract course information from user message if present
    conv_intelligence._extract_course_info(user_message, conversation, analysis)
    
    db.session.commit()
    
    return jsonify({
        'user_message': user_msg.to_dict(),
        'ai_response': ai_msg.to_dict(),
        'conversation_update': {
            'current_step': conversation.current_step,
            'completion_percentage': conversation.completion_percentage,
            'framework_areas_covered': new_areas
        },
        'analysis': {
            'intent': analysis['intent'],
            'confidence': analysis['confidence'],
            'boundary_violation': analysis.get('boundary_violation'),
            'conversation_health': analysis.get('conversation_health'),
            'needs_depth': analysis.get('needs_depth')
        },
        'privacy_notice': 'Your responses help design your course and aren\'t stored permanently or shared',
        'usage_disclaimer': 'This assistant is for educational course design only.'
    })

@conversation_bp.route('/conversations/<session_id>/summary', methods=['GET'])
def get_conversation_summary(session_id):
    """Get a summary of the conversation and course design"""
    conversation = Conversation.query.filter_by(session_id=session_id).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    
    # Generate summary
    summary = {
        'course_design': conversation.to_dict(),
        'framework_coverage': {
            'areas_covered': conversation.get_framework_areas_covered(),
            'completion_percentage': conversation.completion_percentage
        },
        'conversation_stats': {
            'total_messages': len(messages),
            'user_messages': len([m for m in messages if m.sender == 'user']),
            'duration': (conversation.updated_at - conversation.created_at).total_seconds() / 60 if conversation.updated_at and conversation.created_at else 0
        }
    }
    
    return jsonify(summary)

@conversation_bp.route('/framework/concepts', methods=['GET'])
def get_framework_concepts():
    """Get all framework concepts for reference"""
    concepts = FrameworkConcept.query.all()
    return jsonify([concept.to_dict() for concept in concepts])

@conversation_bp.route('/conversations/<session_id>/export', methods=['GET'])
def export_conversation(session_id):
    """Export conversation data in multiple formats"""
    format_type = request.args.get('format', 'json')
    
    conversation = Conversation.query.filter_by(session_id=session_id).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    
    export_data = {
        'conversation': conversation.to_dict(),
        'messages': [msg.to_dict() for msg in messages],
        'export_timestamp': datetime.utcnow().isoformat()
    }
    
    if format_type == 'json':
        return jsonify(export_data)
    elif format_type == 'summary':
        # Return a structured summary for integration
        return jsonify({
            'course_title': conversation.course_title,
            'target_audience': conversation.target_audience,
            'educational_level': conversation.educational_level,
            'learning_objectives': conversation.learning_objectives,
            'assessment_approach': conversation.assessment_approach,
            'delivery_method': conversation.delivery_method,
            'bias_considerations': conversation.bias_considerations,
            'framework_areas_covered': conversation.get_framework_areas_covered(),
            'completion_status': 'complete' if conversation.completion_percentage >= 100 else 'in_progress'
        })
    else:
        return jsonify({'error': 'Unsupported format'}), 400

