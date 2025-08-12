import json
import re
from datetime import datetime

class AdvancedConversationIntelligence:
    def __init__(self):
        self.framework_areas = [
            "Learning Objectives",
            "Target Audience Analysis", 
            "Educational Level Alignment",
            "Assessment Strategy",
            "Course Structure",
            "Bias Elimination",
            "Inclusive Design",
            "Career Relevance"
        ]
        
    def generate_response(self, user_message, conversation_context=None):
        """Generate a framework-guided response"""

    def sanitize_input(self, text):
        return text.strip()
    
    def detect_safety_violations(self, text):
        return []
    
    def analyze_user_message(self, message, history):
        return {'intent': 'course_design', 'confidence': 0.8, 'framework_references': []}
    
    def generate_intelligent_response(self, message, conversation, analysis):
        return "Thanks for your message! I'm here to help you design your AI course using the She Is AI framework."    
        
        # Simple demo responses based on keywords
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['beginner', 'new', 'start']):
            response = """Perfect! Creating an AI course for beginners is exactly what the She Is AI educational framework excels at. 

Let's start by understanding your learners better. Our framework emphasizes inclusive design from the very beginning.

Can you tell me more about:
- What specific background do your learners have? (Complete beginners to programming, or some technical experience?)
- What's their main motivation for learning AI? (Career change, skill enhancement, curiosity?)
- How much time can they realistically dedicate to learning?

This will help us design a course that's truly accessible and engaging for your specific audience."""
            
        elif any(word in user_lower for word in ['machine learning', 'ml', 'algorithms']):
            response = """Excellent choice! Machine learning is a fantastic entry point into AI, and our framework has specific approaches for making complex technical concepts accessible.

For ML courses, the She Is AI methodology emphasizes:
- **Practical application first** - learners see results before diving into theory
- **Real-world examples** that connect to diverse industries and backgrounds
- **Bias awareness** - critical when teaching ML algorithms

What specific ML topics are you most excited to include? For example:
- Supervised learning (classification, regression)
- Data preprocessing and ethics
- Model evaluation and interpretation
- Practical tools (Python, no-code platforms, etc.)

Also, what's the end goal for your learners? Are they aiming for specific careers or just general understanding?"""
            
        elif any(word in user_lower for word in ['career', 'job', 'professional']):
            response = """That's fantastic! Career-focused AI education is at the heart of the She Is AI framework. We believe in creating real pathways to opportunity.

Let's design something that truly prepares learners for the job market. Our framework includes:
- **Industry-relevant projects** that become portfolio pieces
- **Skills mapping** to actual job requirements
- **Inclusive career guidance** that addresses barriers different groups face

A few key questions to shape your course:
- What specific AI career paths are you targeting? (Data scientist, ML engineer, AI product manager, etc.)
- What's the job market like in your region or target area?
- How long do you envision the learning journey? (Bootcamp-style intensive vs. longer-term program)

We'll make sure every lesson connects directly to employable skills and real opportunities."""
            
        else:
            response = """I love your enthusiasm for creating an AI course! The She Is AI framework is designed to help you build something truly impactful and inclusive.

To give you the most relevant guidance, I'd love to understand your vision better:

- **Who are your learners?** (Students, professionals, career changers, etc.)
- **What's their current level?** (Complete beginners, some tech background, etc.)  
- **What's your main goal?** (Career preparation, general education, specific skills, etc.)
- **How will they learn?** (Online, in-person, self-paced, cohort-based, etc.)

The more specific you can be, the better I can help you leverage our framework's proven approaches for inclusive, effective AI education that creates real opportunities for learners."""

        return {
            'content': response,
            'framework_area': self._detect_framework_area(user_message),
            'confidence_score': 0.85,
            'message_type': 'framework_guidance'
        }
    
    def _detect_framework_area(self, message):
        """Detect which framework area the message relates to"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['audience', 'learner', 'student', 'who']):
            return "Target Audience Analysis"
        elif any(word in message_lower for word in ['beginner', 'advanced', 'level', 'experience']):
            return "Educational Level Alignment"
        elif any(word in message_lower for word in ['goal', 'objective', 'outcome', 'learn']):
            return "Learning Objectives"
        elif any(word in message_lower for word in ['assess', 'test', 'evaluation', 'grade']):
            return "Assessment Strategy"
        elif any(word in message_lower for word in ['career', 'job', 'professional', 'work']):
            return "Career Relevance"
        elif any(word in message_lower for word in ['structure', 'organize', 'sequence', 'order']):
            return "Course Structure"
        else:
            return "General Framework Guidance"
    
    def extract_course_info(self, conversation_messages):
        """Extract structured course information from conversation"""
        course_info = {
            'title': None,
            'target_audience': None,
            'educational_level': None,
            'duration': None,
            'learning_objectives': None,
            'assessment_approach': None
        }
        
        # Simple keyword extraction from user messages
        user_messages = [msg['content'] for msg in conversation_messages if msg.get('sender') == 'user']
        all_text = ' '.join(user_messages).lower()
        
        # Extract basic information
        if 'beginner' in all_text:
            course_info['educational_level'] = 'Beginner'
            course_info['target_audience'] = 'Beginners interested in AI'
        
        if 'machine learning' in all_text or 'ml' in all_text:
            course_info['title'] = 'Introduction to Machine Learning'
            
        if 'career' in all_text or 'job' in all_text:
            course_info['learning_objectives'] = 'Prepare learners for AI careers'
            
        return course_info
    
    def sanitize_input(self, user_input):
        """Basic input sanitization"""
        if not user_input or not isinstance(user_input, str):
            return ""
            
        # Remove HTML tags
        clean_input = re.sub(r'<[^>]+>', '', user_input)
        
        # Limit length
        if len(clean_input) > 1000:
            clean_input = clean_input[:1000]
            
        return clean_input.strip()
    
    def check_safety_violations(self, message):
        """Check for safety violations"""
        message_lower = message.lower()
        
        # Simple keyword-based safety check
        inappropriate_keywords = [
            'hack', 'illegal', 'harmful', 'dangerous', 'weapon',
            'violence', 'hate', 'discrimination'
        ]
        
        for keyword in inappropriate_keywords:
            if keyword in message_lower:
                return True, f"I focus specifically on educational course design using the She Is AI framework. Let's keep our conversation centered on creating inclusive, effective AI education."
                
        return False, None

