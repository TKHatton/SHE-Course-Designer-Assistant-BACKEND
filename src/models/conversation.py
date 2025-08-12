from datetime import datetime
import json
from src.models.user import db

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    
    # Course design data
    course_title = db.Column(db.String(200))
    target_audience = db.Column(db.String(100))
    educational_level = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    learning_objectives = db.Column(db.Text)
    assessment_approach = db.Column(db.String(100))
    delivery_method = db.Column(db.String(100))
    bias_considerations = db.Column(db.Text)
    
    # Progress tracking
    current_step = db.Column(db.Integer, default=1)
    total_steps = db.Column(db.Integer, default=10)
    completion_percentage = db.Column(db.Float, default=0.0)
    
    # Framework coverage tracking
    framework_areas_covered = db.Column(db.Text)  # JSON string
    
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status,
            'course_title': self.course_title,
            'target_audience': self.target_audience,
            'educational_level': self.educational_level,
            'duration': self.duration,
            'learning_objectives': self.learning_objectives,
            'assessment_approach': self.assessment_approach,
            'delivery_method': self.delivery_method,
            'bias_considerations': self.bias_considerations,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'completion_percentage': self.completion_percentage,
            'framework_areas_covered': json.loads(self.framework_areas_covered) if self.framework_areas_covered else []
        }
    
    def get_framework_areas_covered(self):
        if self.framework_areas_covered:
            return json.loads(self.framework_areas_covered)
        return []
    
    def set_framework_areas_covered(self, areas):
        self.framework_areas_covered = json.dumps(areas)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message_type = db.Column(db.String(50), default='text')  # text, question, summary, etc.
    
    # Metadata for conversation intelligence
    intent = db.Column(db.String(100))  # question_type, clarification, etc.
    confidence = db.Column(db.Float)
    framework_references = db.Column(db.Text)  # JSON string of referenced framework concepts
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'message_type': self.message_type,
            'intent': self.intent,
            'confidence': self.confidence,
            'framework_references': json.loads(self.framework_references) if self.framework_references else []
        }
    
    def get_framework_references(self):
        if self.framework_references:
            return json.loads(self.framework_references)
        return []
    
    def set_framework_references(self, references):
        self.framework_references = json.dumps(references)

class FrameworkConcept(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # philosophy, lesson_structure, assessment, etc.
    description = db.Column(db.Text)
    examples = db.Column(db.Text)  # JSON string
    level_adaptations = db.Column(db.Text)  # JSON string
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'examples': json.loads(self.examples) if self.examples else [],
            'level_adaptations': json.loads(self.level_adaptations) if self.level_adaptations else {}
        }

