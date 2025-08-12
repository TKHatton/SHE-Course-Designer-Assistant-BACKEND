from flask import Blueprint, request, jsonify, send_file
from src.models.conversation import Conversation, Message
from src.models.user import db
import json
import csv
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import os

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
            return export_as_pdf(conversation, messages)
        else:
            return jsonify({'error': 'Unsupported format. Use json, csv, or pdf'}), 400
            
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
    
    # Create response
    response = send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'course_design_{conversation.session_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )
    
    return response

def export_as_pdf(conversation, messages):
    """Export conversation as PDF"""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    try:
        # Create PDF document
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2563eb')
        )
        story.append(Paragraph("She Is AI Course Design Summary", title_style))
        story.append(Spacer(1, 20))
        
        # Course Information
        if conversation.course_title:
            story.append(Paragraph(f"<b>Course Title:</b> {conversation.course_title}", styles['Normal']))
        if conversation.target_audience:
            story.append(Paragraph(f"<b>Target Audience:</b> {conversation.target_audience}", styles['Normal']))
        if conversation.educational_level:
            story.append(Paragraph(f"<b>Educational Level:</b> {conversation.educational_level}", styles['Normal']))
        if conversation.duration:
            story.append(Paragraph(f"<b>Duration:</b> {conversation.duration}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Progress Information
        progress_data = [
            ['Progress Metric', 'Value'],
            ['Completion Percentage', f"{conversation.completion_percentage}%"],
            ['Current Step', f"{conversation.current_step} of {conversation.total_steps}"],
            ['Status', conversation.status.title()],
            ['Created', conversation.created_at.strftime('%Y-%m-%d %H:%M')],
            ['Last Updated', conversation.updated_at.strftime('%Y-%m-%d %H:%M')]
        ]
        
        progress_table = Table(progress_data)
        progress_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("<b>Course Design Progress</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(progress_table)
        story.append(Spacer(1, 20))
        
        # Learning Objectives
        if conversation.learning_objectives:
            story.append(Paragraph("<b>Learning Objectives</b>", styles['Heading2']))
            story.append(Spacer(1, 10))
            story.append(Paragraph(conversation.learning_objectives, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Assessment Approach
        if conversation.assessment_approach:
            story.append(Paragraph("<b>Assessment Approach</b>", styles['Heading2']))
            story.append(Spacer(1, 10))
            story.append(Paragraph(conversation.assessment_approach, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Conversation Messages
        story.append(Paragraph("<b>Design Conversation</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for msg in messages:
            if msg.sender == 'user':
                sender_style = ParagraphStyle(
                    'UserMessage',
                    parent=styles['Normal'],
                    leftIndent=20,
                    textColor=colors.HexColor('#1e40af'),
                    fontName='Helvetica-Bold'
                )
                story.append(Paragraph(f"<b>You:</b> {msg.content}", sender_style))
            else:
                sender_style = ParagraphStyle(
                    'AssistantMessage',
                    parent=styles['Normal'],
                    leftIndent=20,
                    textColor=colors.HexColor('#059669')
                )
                story.append(Paragraph(f"<b>Assistant:</b> {msg.content}", sender_style))
            
            story.append(Spacer(1, 10))
        
        # Framework Coverage
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Framework Coverage Analysis</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        coverage = get_framework_coverage(conversation)
        for area, status in coverage.items():
            status_text = "✓ Covered" if status else "○ Not Covered"
            story.append(Paragraph(f"<b>{area}:</b> {status_text}", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(
            f"Generated by She Is AI Course Design Assistant on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            "This document contains your course design session summary.",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
        
        # Send file
        return send_file(
            temp_file.name,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'course_design_{conversation.session_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

def get_framework_coverage(conversation):
    """Analyze framework coverage based on conversation"""
    # This would be enhanced with actual framework analysis
    # For now, return basic coverage based on conversation data
    coverage = {
        'Learning Objectives': bool(conversation.learning_objectives),
        'Target Audience Analysis': bool(conversation.target_audience),
        'Educational Level Alignment': bool(conversation.educational_level),
        'Assessment Strategy': bool(conversation.assessment_approach),
        'Course Structure': bool(conversation.duration),
        'Bias Elimination': False,  # Would be determined by message analysis
        'Inclusive Design': False,  # Would be determined by message analysis
        'Career Relevance': False,  # Would be determined by message analysis
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
    # This would use NLP to extract key themes and insights
    # For now, return basic insights
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

