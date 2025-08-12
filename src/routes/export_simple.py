from flask import Blueprint, request, jsonify
from src.models.conversation import Conversation, Message
import json
import csv
import io
from datetime import datetime

export_bp = Blueprint('export', __name__)

@export_bp.route('/conversations/<session_id>/export', methods=['GET'])
def export_conversation(session_id):
    """Export conversation data in various formats"""
    try:
        format_type = request.args.get('format', 'json').lower()
        
        # Get conversation and messages
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
            
        messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
        
        if format_type == 'json':
            return export_as_json(conversation, messages)
        elif format_type == 'csv':
            return export_as_csv(conversation, messages)
        elif format_type == 'pdf':
            return jsonify({'error': 'PDF export temporarily unavailable. Please use JSON or CSV format.'}), 400
        else:
            return jsonify({'error': 'Unsupported format. Use json or csv'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def export_as_json(conversation, messages):
    """Export conversation as JSON"""
    data = {
        'conversation_metadata': {
            'session_id': conversation.session_id,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'status': conversation.status,
            'course_title': conversation.course_title,
            'target_audience': conversation.target_audience,
            'educational_level': conversation.educational_level,
            'duration': conversation.duration,
            'learning_objectives': conversation.learning_objectives,
            'assessment_approach': conversation.assessment_approach,
            'completion_percentage': conversation.completion_percentage,
            'current_step': conversation.current_step,
            'total_steps': conversation.total_steps
        },
        'messages': [
            {
                'id': msg.id,
                'sender': msg.sender,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'message_type': msg.message_type,
                'framework_area': msg.framework_area,
                'confidence_score': msg.confidence_score
            }
            for msg in messages
        ],
        'framework_coverage': get_framework_coverage(conversation),
        'export_metadata': {
            'exported_at': datetime.utcnow().isoformat(),
            'export_format': 'json',
            'total_messages': len(messages),
            'framework': 'She Is AI Educational Framework'
        }
    }
    
    return jsonify(data)

def export_as_csv(conversation, messages):
    """Export conversation as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'Message ID', 'Sender', 'Content', 'Timestamp', 'Message Type', 
        'Framework Area', 'Confidence Score'
    ])
    
    # Write message data
    for msg in messages:
        writer.writerow([
            msg.id,
            msg.sender,
            msg.content,
            msg.timestamp.isoformat(),
            msg.message_type or '',
            msg.framework_area or '',
            msg.confidence_score or ''
        ])
    
    output.seek(0)
    csv_data = output.getvalue()
    
    response = jsonify({
        'csv_data': csv_data,
        'filename': f'course_design_{conversation.session_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    })
    
    return response

def get_framework_coverage(conversation):
    """Analyze framework coverage based on conversation"""
    coverage = {
        'Learning Objectives': bool(conversation.learning_objectives),
        'Target Audience Analysis': bool(conversation.target_audience),
        'Educational Level Alignment': bool(conversation.educational_level),
        'Assessment Strategy': bool(conversation.assessment_approach),
        'Course Structure': bool(conversation.duration),
        'Bias Elimination': False,
        'Inclusive Design': False,
        'Career Relevance': False,
    }
    return coverage

@export_bp.route('/conversations/<session_id>/summary', methods=['GET'])
def get_conversation_summary(session_id):
    """Get a structured summary of the conversation for integration"""
    try:
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
            
        messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
        
        # Generate structured summary
        summary = {
            'course_design': {
                'title': conversation.course_title,
                'target_audience': conversation.target_audience,
                'educational_level': conversation.educational_level,
                'duration': conversation.duration,
                'learning_objectives': conversation.learning_objectives,
                'assessment_approach': conversation.assessment_approach
            },
            'progress': {
                'completion_percentage': conversation.completion_percentage,
                'current_step': conversation.current_step,
                'total_steps': conversation.total_steps,
                'status': conversation.status
            },
            'framework_analysis': get_framework_coverage(conversation),
            'quality_metrics': {
                'total_messages': len(messages),
                'user_messages': len([m for m in messages if m.sender == 'user']),
                'assistant_messages': len([m for m in messages if m.sender == 'assistant']),
                'average_confidence': calculate_average_confidence(messages),
                'completeness_score': calculate_completeness_score(conversation)
            },
            'key_insights': extract_key_insights(messages),
            'recommendations': generate_recommendations(conversation, messages)
        }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_average_confidence(messages):
    """Calculate average confidence score from messages"""
    confidence_scores = [m.confidence_score for m in messages if m.confidence_score is not None]
    return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

def calculate_completeness_score(conversation):
    """Calculate how complete the course design is"""
    required_fields = [
        conversation.course_title,
        conversation.target_audience,
        conversation.educational_level,
        conversation.learning_objectives,
        conversation.assessment_approach
    ]
    
    completed_fields = sum(1 for field in required_fields if field)
    return (completed_fields / len(required_fields)) * 100

def extract_key_insights(messages):
    """Extract key insights from the conversation"""
    user_messages = [m.content for m in messages if m.sender == 'user']
    
    insights = []
    if any('beginner' in msg.lower() for msg in user_messages):
        insights.append("Course targets beginner-level learners")
    if any('practical' in msg.lower() or 'hands-on' in msg.lower() for msg in user_messages):
        insights.append("Emphasis on practical, hands-on learning")
    if any('career' in msg.lower() or 'job' in msg.lower() for msg in user_messages):
        insights.append("Focus on career development and job readiness")
    
    return insights

def generate_recommendations(conversation, messages):
    """Generate recommendations for course improvement"""
    recommendations = []
    
    if not conversation.learning_objectives:
        recommendations.append("Define clear, measurable learning objectives")
    
    if not conversation.assessment_approach:
        recommendations.append("Develop a comprehensive assessment strategy")
    
    if conversation.completion_percentage < 50:
        recommendations.append("Continue the design process to cover more framework areas")
    
    return recommendations

