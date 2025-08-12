from src.models.conversation import db, FrameworkConcept
import json

def seed_framework_concepts():
    """Seed the database with She Is AI framework concepts"""
    
    concepts = [
        {
            'name': 'Universal Accessibility',
            'category': 'philosophy',
            'description': 'Every component is designed to be accessible regardless of prior technical experience, economic background, or geographic location.',
            'examples': ['Low-tech and no-tech alternatives', 'Multiple learning modalities', 'Flexible scheduling options'],
            'level_adaptations': {
                'elementary': 'Simple, age-appropriate activities',
                'secondary': 'Technology options with alternatives',
                'college': 'Professional tools with training',
                'professional': 'Industry-standard platforms',
                'corporate': 'Enterprise-level accessibility'
            }
        },
        {
            'name': 'Bias-Free by Design',
            'category': 'philosophy',
            'description': 'Framework constructed with explicit goal of eliminating bias at every level, from content creation to assessment methods.',
            'examples': ['Diverse representation in materials', 'Inclusive language protocols', 'Equitable assessment methods'],
            'level_adaptations': {
                'elementary': 'Simple fairness concepts',
                'secondary': 'Critical evaluation of bias',
                'college': 'Technical bias mitigation',
                'professional': 'Organizational bias strategies',
                'corporate': 'Systematic bias elimination'
            }
        },
        {
            'name': 'Portfolio-Driven Learning',
            'category': 'philosophy',
            'description': 'Assessment through authentic applications that create valuable assets for career advancement.',
            'examples': ['Digital portfolios', 'Project-based assessment', 'Career-relevant artifacts'],
            'level_adaptations': {
                'elementary': 'Creative projects and stories',
                'secondary': 'Research presentations and applications',
                'college': 'Professional-grade case studies',
                'professional': 'Industry portfolios',
                'corporate': 'Implementation plans'
            }
        },
        {
            'name': 'Community-Centered Learning',
            'category': 'philosophy',
            'description': 'Building strong learning communities that provide ongoing support and professional networking.',
            'examples': ['Peer collaboration', 'Mentorship programs', 'Professional networks'],
            'level_adaptations': {
                'elementary': 'Classroom community building',
                'secondary': 'Study groups and peer support',
                'college': 'Professional network development',
                'professional': 'Industry connections',
                'corporate': 'Organizational learning communities'
            }
        },
        {
            'name': 'Career-Connected Education',
            'category': 'philosophy',
            'description': 'Every element explicitly connected to career opportunities and professional development.',
            'examples': ['Industry partnerships', 'Career pathway mapping', 'Professional skill development'],
            'level_adaptations': {
                'elementary': 'Career exploration activities',
                'secondary': 'College and career preparation',
                'college': 'Job readiness training',
                'professional': 'Career advancement',
                'corporate': 'Leadership development'
            }
        },
        {
            'name': 'Opening Ritual',
            'category': 'lesson_structure',
            'description': 'Community building and intention setting that reinforces SHE IS AI values and creates belonging (5 min).',
            'examples': ['Circle time', 'Affirmations', 'Intention setting'],
            'level_adaptations': {
                'elementary': 'Interactive circle time with movement and music',
                'secondary': 'Goal setting and community check-in',
                'college': 'Professional intention setting',
                'professional': 'Career goal alignment',
                'corporate': 'Team alignment activities'
            }
        },
        {
            'name': 'Learning Objectives',
            'category': 'lesson_structure',
            'description': 'Clear, specific goals connected to broader career and life relevance for each educational level (3 min).',
            'examples': ['SMART goals', 'Career connections', 'Life relevance'],
            'level_adaptations': {
                'elementary': 'Simple, concrete learning goals',
                'secondary': 'Academic and career-connected objectives',
                'college': 'Professional competency goals',
                'professional': 'Industry-specific outcomes',
                'corporate': 'Organizational objectives'
            }
        },
        {
            'name': 'Core Content Delivery',
            'category': 'lesson_structure',
            'description': 'Multi-modal content delivery adapted for different developmental stages and learning preferences (Variable time).',
            'examples': ['Visual presentations', 'Interactive demonstrations', 'Hands-on activities'],
            'level_adaptations': {
                'elementary': 'Storytelling, games, and exploration',
                'secondary': 'Interactive lectures and discussions',
                'college': 'Professional case studies',
                'professional': 'Industry applications',
                'corporate': 'Strategic implementations'
            }
        },
        {
            'name': 'Hands-On Practice',
            'category': 'lesson_structure',
            'description': 'Immediate application of new knowledge through authentic, engaging activities (30% of time).',
            'examples': ['Practical exercises', 'Tool exploration', 'Skill practice'],
            'level_adaptations': {
                'elementary': 'Creative play and exploration',
                'secondary': 'Project-based activities',
                'college': 'Professional tool usage',
                'professional': 'Workplace applications',
                'corporate': 'Strategic implementations'
            }
        },
        {
            'name': 'Project Work Time',
            'category': 'lesson_structure',
            'description': 'Portfolio development through meaningful projects that demonstrate learning and build career assets (15+ min sessions).',
            'examples': ['Portfolio projects', 'Capstone work', 'Career artifacts'],
            'level_adaptations': {
                'elementary': 'Creative projects and presentations',
                'secondary': 'Research and advocacy projects',
                'college': 'Professional portfolio development',
                'professional': 'Industry case studies',
                'corporate': 'Implementation planning'
            }
        },
        {
            'name': 'Reflection & Action Planning',
            'category': 'lesson_structure',
            'description': 'Consolidation of learning and explicit connection to personal and professional goals (10 min).',
            'examples': ['Learning journals', 'Goal setting', 'Action plans'],
            'level_adaptations': {
                'elementary': 'Simple reflection activities',
                'secondary': 'Academic and career planning',
                'college': 'Professional development planning',
                'professional': 'Career advancement strategies',
                'corporate': 'Strategic planning'
            }
        },
        {
            'name': 'Closing/Commitment',
            'category': 'lesson_structure',
            'description': 'Community reinforcement and clear next steps for continued learning and engagement (2 min).',
            'examples': ['Commitment statements', 'Next steps', 'Community support'],
            'level_adaptations': {
                'elementary': 'Simple commitments and celebrations',
                'secondary': 'Academic and personal commitments',
                'college': 'Professional commitments',
                'professional': 'Career commitments',
                'corporate': 'Organizational commitments'
            }
        },
        {
            'name': 'AI in Context',
            'category': 'content_progression',
            'description': 'How AI shapes this field/topic? (e.g., tools, workflows, industry examples)',
            'examples': ['Industry applications', 'Workflow integration', 'Real-world examples'],
            'level_adaptations': {
                'elementary': 'AI in daily life examples',
                'secondary': 'AI in academic and career contexts',
                'college': 'Professional AI applications',
                'professional': 'Industry-specific AI tools',
                'corporate': 'Organizational AI strategy'
            }
        },
        {
            'name': 'Ethics & Responsible AI Use',
            'category': 'content_progression',
            'description': 'Designing safe, fair, and trustworthy AI experiences.',
            'examples': ['Ethical guidelines', 'Safety protocols', 'Trust frameworks'],
            'level_adaptations': {
                'elementary': 'Basic fairness and safety concepts',
                'secondary': 'Ethical decision-making frameworks',
                'college': 'Professional ethics standards',
                'professional': 'Industry compliance',
                'corporate': 'Organizational ethics policies'
            }
        },
        {
            'name': 'Bias Recognition & Equity in AI',
            'category': 'content_progression',
            'description': 'Spotting bias and designing equitable AI systems.',
            'examples': ['Bias detection methods', 'Equity frameworks', 'Inclusive design'],
            'level_adaptations': {
                'elementary': 'Simple fairness examples',
                'secondary': 'Critical evaluation skills',
                'college': 'Technical bias analysis',
                'professional': 'Bias mitigation strategies',
                'corporate': 'Systematic bias elimination'
            }
        },
        {
            'name': 'AI Skills for the Future',
            'category': 'content_progression',
            'description': 'The AI-related skills learners will develop for career readiness.',
            'examples': ['Technical skills', 'Critical thinking', 'Collaboration'],
            'level_adaptations': {
                'elementary': 'Basic technology literacy',
                'secondary': 'Academic and career preparation',
                'college': 'Professional skill development',
                'professional': 'Advanced competencies',
                'corporate': 'Leadership capabilities'
            }
        },
        {
            'name': "Women's Role in Shaping AI",
            'category': 'content_progression',
            'description': 'Highlighting contributions and leadership of women in AI.',
            'examples': ['Role model profiles', 'Historical contributions', 'Current leaders'],
            'level_adaptations': {
                'elementary': 'Inspiring stories and role models',
                'secondary': 'Career pathway examples',
                'college': 'Professional mentorship',
                'professional': 'Leadership development',
                'corporate': 'Organizational leadership'
            }
        },
        {
            'name': 'Visual Learning Integration',
            'category': 'teaching_methods',
            'description': 'Colorful graphics, animations, interactive media, data visualizations, and professional-quality infographics adapted for different developmental stages.',
            'examples': ['Infographics', 'Interactive media', 'Data visualizations'],
            'level_adaptations': {
                'elementary': 'Colorful, engaging visuals',
                'secondary': 'Educational infographics',
                'college': 'Professional presentations',
                'professional': 'Industry-standard visuals',
                'corporate': 'Executive dashboards'
            }
        },
        {
            'name': 'Hands-On Learning Implementation',
            'category': 'teaching_methods',
            'description': 'Exploration and creativity through simple AI tools progressing to professional-grade applications and workplace environments.',
            'examples': ['Tool exploration', 'Creative projects', 'Practical applications'],
            'level_adaptations': {
                'elementary': 'Simple AI-powered tools',
                'secondary': 'Educational AI platforms',
                'college': 'Professional AI tools',
                'professional': 'Industry applications',
                'corporate': 'Enterprise solutions'
            }
        },
        {
            'name': 'Collaborative Learning Structures',
            'category': 'teaching_methods',
            'description': 'Building social skills and community while exploring AI concepts together, progressing to professional network development.',
            'examples': ['Group projects', 'Peer learning', 'Community building'],
            'level_adaptations': {
                'elementary': 'Collaborative play and learning',
                'secondary': 'Study groups and projects',
                'college': 'Professional collaboration',
                'professional': 'Industry networking',
                'corporate': 'Team development'
            }
        },
        {
            'name': 'Problem-Based Learning Applications',
            'category': 'teaching_methods',
            'description': 'Real-world challenges from age-appropriate community problems to complex industry-relevant challenges.',
            'examples': ['Case studies', 'Real-world problems', 'Industry challenges'],
            'level_adaptations': {
                'elementary': 'Community helper scenarios',
                'secondary': 'Social issue projects',
                'college': 'Professional case studies',
                'professional': 'Industry challenges',
                'corporate': 'Strategic problems'
            }
        },
        {
            'name': 'Portfolio-Based Assessment Integration',
            'category': 'teaching_methods',
            'description': 'Continuous building of tangible evidence of skills and knowledge for academic and career advancement.',
            'examples': ['Digital portfolios', 'Project collections', 'Career artifacts'],
            'level_adaptations': {
                'elementary': 'Creative project collections',
                'secondary': 'Academic portfolios',
                'college': 'Professional portfolios',
                'professional': 'Career advancement portfolios',
                'corporate': 'Leadership portfolios'
            }
        },
        {
            'name': 'Authentic Application Over Abstract Testing',
            'category': 'assessment',
            'description': 'Demonstrate knowledge through real-world applications rather than artificial testing situations.',
            'examples': ['Project-based assessment', 'Real-world applications', 'Practical demonstrations'],
            'level_adaptations': {
                'elementary': 'Creative demonstrations',
                'secondary': 'Project presentations',
                'college': 'Professional applications',
                'professional': 'Workplace implementations',
                'corporate': 'Strategic applications'
            }
        },
        {
            'name': 'Portfolio Development as Learning Process',
            'category': 'assessment',
            'description': 'Integrated throughout learning rather than separate assessment activity, building professional skills.',
            'examples': ['Continuous portfolio building', 'Reflective practice', 'Skill documentation'],
            'level_adaptations': {
                'elementary': 'Simple project documentation',
                'secondary': 'Academic portfolio development',
                'college': 'Professional portfolio creation',
                'professional': 'Career portfolio management',
                'corporate': 'Leadership portfolio development'
            }
        },
        {
            'name': 'Peer Evaluation and Collaborative Assessment',
            'category': 'assessment',
            'description': 'Structured peer review processes that build critical thinking skills and community support.',
            'examples': ['Peer feedback', 'Collaborative evaluation', 'Community assessment'],
            'level_adaptations': {
                'elementary': 'Simple peer sharing',
                'secondary': 'Structured peer review',
                'college': 'Professional peer evaluation',
                'professional': 'Industry peer assessment',
                'corporate': 'Team evaluation processes'
            }
        },
        {
            'name': 'Content-Level Bias Elimination',
            'category': 'bias_elimination',
            'description': 'Systematic bias elimination protocols ensuring diverse representation, inclusive language, and equitable treatment of different perspectives.',
            'examples': ['Diverse representation', 'Inclusive language', 'Equitable perspectives'],
            'level_adaptations': {
                'elementary': 'Diverse characters and stories',
                'secondary': 'Multiple perspective inclusion',
                'college': 'Professional diversity standards',
                'professional': 'Industry inclusion practices',
                'corporate': 'Organizational diversity policies'
            }
        },
        {
            'name': 'Instructional Design Bias Elimination',
            'category': 'bias_elimination',
            'description': 'Learning activities, assessment methods, and support systems designed to counteract historical exclusion of women and underrepresented groups.',
            'examples': ['Inclusive activities', 'Equitable assessment', 'Supportive systems'],
            'level_adaptations': {
                'elementary': 'Inclusive learning activities',
                'secondary': 'Equitable participation methods',
                'college': 'Professional inclusion strategies',
                'professional': 'Workplace equity practices',
                'corporate': 'Organizational inclusion systems'
            }
        },
        {
            'name': 'Community and Culture Bias Elimination',
            'category': 'bias_elimination',
            'description': 'Learning communities that actively promote inclusion and equity while providing safe spaces for exploration and development.',
            'examples': ['Safe learning spaces', 'Inclusive communities', 'Equity promotion'],
            'level_adaptations': {
                'elementary': 'Safe classroom environments',
                'secondary': 'Inclusive school communities',
                'college': 'Professional learning communities',
                'professional': 'Workplace inclusion',
                'corporate': 'Organizational culture change'
            }
        }
    ]
    
    for concept_data in concepts:
        concept = FrameworkConcept(
            name=concept_data['name'],
            category=concept_data['category'],
            description=concept_data['description'],
            examples=json.dumps(concept_data['examples']),
            level_adaptations=json.dumps(concept_data['level_adaptations'])
        )
        db.session.add(concept)
    
    db.session.commit()
    print(f"Seeded {len(concepts)} framework concepts")

