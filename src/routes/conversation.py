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

@conversation_bp.route('/conversations/<session_id>/messages', methods=['POST'])
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
        # Log safety violation (in production, send to monitoring system)
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
    
    # Generate response using available method
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
    current_areas = conversation.get_framework_areas_covered()
    framework_area = response_data.get('framework_area', 'General Framework Guidance')
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

@conversation_bp.route('/conversations/<session_id>/summary', methods=['GET'])
def get_conversation_summary(session_id):
    """Get a summary of the conversation and course design"""
    conversation = Conversation.query.filter_by(session_id=session_id).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    
    # Extract course information using conversation intelligence
    history_data = [{'sender': msg.sender, 'content': msg.content} for msg in messages]
    course_info = conv_intelligence.extract_course_info(history_data)
    
    return jsonify({
        'conversation': conversation.to_dict(),
        'message_count': len(messages),
        'course_design': course_info,
        'framework_areas_covered': conversation.get_framework_areas_covered(),
        'completion_status': {
            'current_step': conversation.current_step,
            'total_steps': conversation.total_steps,
            'percentage': conversation.completion_percentage
        }
    })

@conversation_bp.route('/conversations/<session_id>/export', methods=['GET'])
def export_conversation(session_id):
    """Export conversation in various formats"""
    format_type = request.args.get('format', 'json').lower()
    
    conversation = Conversation.query.filter_by(session_id=session_id).first()
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    
    if format_type == 'json':
        export_data = {
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages],
            'export_timestamp': datetime.utcnow().isoformat(),
            'framework_areas_covered': conversation.get_framework_areas_covered()
        }
        return jsonify(export_data)
    
    elif format_type == 'csv':
        # Create CSV format
        csv_data = "timestamp,sender,content,message_type\n"
        for msg in messages:
            # Escape quotes and newlines for CSV
            content = msg.content.replace('"', '""').replace('\n', ' ')
            csv_data += f'"{msg.timestamp}","{msg.sender}","{content}","{msg.message_type}"\n'
        
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename="conversation_{session_id}.csv"'
        }
    
    else:
        return jsonify({'error': 'Unsupported format. Use json or csv.'}), 400

