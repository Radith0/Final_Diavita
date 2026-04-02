"""
Reports API Routes - Generate comprehensive PDF reports using LLM
"""
from flask import Blueprint, request, jsonify, send_file
from models.database import db
from models.database.user import User
from models.database.analysis_result import AnalysisResult
from utils.auth import jwt_required
from models.llm.llm_interface import GroqLLMInterface
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)
llm = GroqLLMInterface()

# Helper to run async functions in sync context
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@reports_bp.route('/generate-pdf/<int:result_id>', methods=['GET'])
@jwt_required
def generate_pdf_report(result_id):
    """
    Generate a comprehensive PDF report using LLM for personalized content
    """
    try:
        current_user = request.current_user
        user_id = current_user['user_id']
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get the analysis result
        result = AnalysisResult.query.filter_by(
            id=result_id,
            user_id=user_id
        ).first()

        if not result:
            return jsonify({'error': 'Analysis result not found'}), 404

        # Generate LLM-powered report content
        logger.info(f"Generating LLM report for user {user_id}, result {result_id}")
        report_content = generate_llm_report_content(user, result)

        # Create PDF
        buffer = BytesIO()
        pdf = create_pdf_report(buffer, user, result, report_content)
        buffer.seek(0)

        # Return PDF as download
        filename = f"DIAVITA_Health_Report_{user.username}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF report', 'message': str(e)}), 500


def generate_llm_report_content(user, result):
    """
    Use LLM to generate personalized, comprehensive report content
    """
    # Prepare data for LLM
    lifestyle_data = result.lifestyle_data or {}
    detailed_results = result.detailed_results or {}

    risk_score = result.combined_risk
    retinal_risk = result.retinal_risk
    lifestyle_risk = result.lifestyle_risk
    risk_category = result.risk_category

    # Create comprehensive prompt for LLM
    prompt = f"""You are a medical AI assistant generating a comprehensive diabetes risk assessment report for a patient.

PATIENT INFORMATION:
- Name: {user.username}
- Assessment Date: {result.created_at.strftime('%B %d, %Y')}

RISK ASSESSMENT RESULTS:
- Overall Diabetes Risk Score: {risk_score:.1f}%
- Risk Category: {risk_category}
- Retinal Analysis Risk: {retinal_risk:.1f}%
- Lifestyle Factors Risk: {lifestyle_risk:.1f}%
- Confidence Score: {(result.confidence_score * 100):.0f}%

HEALTH METRICS:
- Age: {lifestyle_data.get('age', 'N/A')} years
- Gender: {lifestyle_data.get('gender', 'N/A')}
- BMI: {lifestyle_data.get('bmi', 'N/A')}
- Blood Pressure: {lifestyle_data.get('systolic_bp', 'N/A')}/{lifestyle_data.get('diastolic_bp', 'N/A')} mmHg
- HbA1c: {lifestyle_data.get('HbA1c', 'N/A')}%
- Blood Glucose: {lifestyle_data.get('blood_glucose', 'N/A')} mg/dL
- HDL Cholesterol: {lifestyle_data.get('hdl_cholesterol', 'N/A')} mg/dL

LIFESTYLE FACTORS:
- Physical Activity: {lifestyle_data.get('physical_activity', 'N/A')} min/week
- Sleep: {lifestyle_data.get('sleep_hours', 'N/A')} hours/night
- Smoking: {lifestyle_data.get('smoking', 'N/A')}
- Alcohol: {lifestyle_data.get('alcohol', 'N/A')}
- Stress Level: {lifestyle_data.get('stress_level', 'N/A')}
- Diet Quality: {lifestyle_data.get('diet_quality', 'N/A')}

MEDICAL HISTORY:
- Hypertension: {lifestyle_data.get('has_hypertension', False)}
- On Cholesterol Medication: {lifestyle_data.get('takes_cholesterol_med', False)}
- Family History of Diabetes: {lifestyle_data.get('family_diabetes_history', False)}

Generate a comprehensive medical report with the following sections in JSON format:

{{
  "executive_summary": "2-3 sentence summary of the patient's overall health status and diabetes risk",
  "risk_interpretation": "Detailed explanation of what their {risk_score:.1f}% risk score means in practical terms",
  "key_findings": [
    "List 4-6 most important findings from the assessment"
  ],
  "risk_factors_identified": [
    "List specific risk factors present with brief explanations"
  ],
  "retinal_analysis_summary": "Summary of retinal image findings and their significance",
  "lifestyle_analysis_summary": "Summary of lifestyle factors impact on diabetes risk",
  "personalized_recommendations": {{
    "immediate_actions": ["3-4 actions to take within next 2 weeks"],
    "short_term_goals": ["3-4 goals for next 3 months"],
    "long_term_strategy": ["3-4 strategies for sustainable health improvement"]
  }},
  "intervention_impact": {{
    "without_intervention": {{
      "6_months": "Expected risk progression and health implications",
      "12_months": "Expected risk progression and health implications"
    }},
    "with_intervention": {{
      "3_months": "Expected improvements with lifestyle changes",
      "6_months": "Expected improvements with lifestyle changes",
      "12_months": "Expected improvements with lifestyle changes"
    }}
  }},
  "specific_dietary_guidance": ["5-6 specific dietary recommendations tailored to their profile"],
  "exercise_prescription": ["4-5 exercise recommendations with specific activities and durations"],
  "monitoring_plan": ["4-5 specific metrics to monitor and how often"],
  "warning_signs": ["4-5 warning signs that require immediate medical attention"],
  "success_stories": "Brief motivational message about others who successfully reduced diabetes risk",
  "resources": ["3-4 helpful resources or organizations for diabetes prevention"]
}}

Important: Be specific, actionable, and personalized based on their exact metrics. Use medical terminology appropriately but keep language accessible. Be encouraging but honest about risks."""

    try:
        # Generate LLM response (async)
        llm_response = run_async(llm.generate(prompt, temperature=0.7, max_tokens=2000))

        # Parse JSON response
        content = json.loads(llm_response)
        logger.info("LLM report content generated successfully")
        return content

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        # Return fallback structured content
        return generate_fallback_content(result, lifestyle_data)
    except Exception as e:
        logger.error(f"LLM report generation failed: {e}")
        return generate_fallback_content(result, lifestyle_data)


def generate_fallback_content(result, lifestyle_data):
    """Fallback content if LLM fails"""
    risk_score = result.combined_risk

    return {
        "executive_summary": f"Your diabetes risk assessment shows a {risk_score:.1f}% risk score, indicating {result.risk_category} risk level.",
        "risk_interpretation": f"This score represents your estimated probability of developing diabetes-related complications if current health patterns continue.",
        "key_findings": [
            f"Overall risk score: {risk_score:.1f}%",
            f"Retinal analysis: {result.retinal_risk:.1f}% risk",
            f"Lifestyle factors: {result.lifestyle_risk:.1f}% risk"
        ],
        "risk_factors_identified": ["Multiple risk factors detected - see detailed analysis"],
        "retinal_analysis_summary": "Retinal imaging analysis completed using AI models.",
        "lifestyle_analysis_summary": "Lifestyle factors evaluated based on provided health data.",
        "personalized_recommendations": {
            "immediate_actions": [
                "Schedule medical consultation",
                "Begin tracking blood glucose",
                "Review current medications"
            ],
            "short_term_goals": [
                "Improve diet quality",
                "Increase physical activity",
                "Optimize sleep schedule"
            ],
            "long_term_strategy": [
                "Maintain healthy weight",
                "Regular health monitoring",
                "Sustainable lifestyle changes"
            ]
        },
        "intervention_impact": {
            "without_intervention": {
                "6_months": f"Risk may increase to {min(100, risk_score + 5):.1f}%",
                "12_months": f"Risk may increase to {min(100, risk_score + 12):.1f}%"
            },
            "with_intervention": {
                "3_months": f"Risk could reduce to {max(0, risk_score - 8):.1f}%",
                "6_months": f"Risk could reduce to {max(0, risk_score - 18):.1f}%",
                "12_months": f"Risk could reduce to {max(0, risk_score - 30):.1f}%"
            }
        },
        "specific_dietary_guidance": [
            "Reduce refined sugar intake",
            "Increase fiber consumption",
            "Control portion sizes",
            "Choose low glycemic index foods"
        ],
        "exercise_prescription": [
            "150 minutes moderate activity per week",
            "Include strength training 2x/week",
            "Daily walking after meals"
        ],
        "monitoring_plan": [
            "Check blood glucose weekly",
            "Monitor blood pressure regularly",
            "Track weight monthly",
            "Annual eye exams"
        ],
        "warning_signs": [
            "Excessive thirst or urination",
            "Unexplained weight loss",
            "Blurred vision",
            "Slow-healing wounds"
        ],
        "success_stories": "Many individuals have successfully reduced their diabetes risk through lifestyle modifications.",
        "resources": [
            "American Diabetes Association",
            "CDC Diabetes Prevention Program",
            "Local diabetes support groups"
        ]
    }


def create_pdf_report(buffer, user, result, llm_content):
    """
    Create a professional PDF report using ReportLab with LLM-generated content
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=6
    )

    # Header
    story.append(Paragraph('DIAVITA', title_style))
    story.append(Paragraph('Comprehensive Diabetes Risk Assessment Report', styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    # Patient Information
    patient_info = f"""
    <b>Patient:</b> {user.username}<br/>
    <b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
    <b>Assessment ID:</b> {result.id}<br/>
    <b>Report Valid Until:</b> {(datetime.now().replace(month=datetime.now().month + 3)).strftime('%B %d, %Y')}
    """
    story.append(Paragraph(patient_info, body_style))
    story.append(Spacer(1, 0.3*inch))

    # Executive Summary Box
    story.append(Paragraph('EXECUTIVE SUMMARY', heading_style))

    # Risk Score Table
    risk_color = colors.green if result.combined_risk < 25 else \
                 colors.orange if result.combined_risk < 50 else \
                 colors.orangered if result.combined_risk < 75 else colors.red

    risk_table_data = [
        ['Overall Diabetes Risk', f'{result.combined_risk:.1f}%'],
        ['Risk Category', result.risk_category.upper()],
        ['Retinal Analysis Risk', f'{result.retinal_risk:.1f}%'],
        ['Lifestyle Factors Risk', f'{result.lifestyle_risk:.1f}%'],
        ['Assessment Confidence', f'{(result.confidence_score * 100):.0f}%']
    ]

    risk_table = Table(risk_table_data, colWidths=[3*inch, 2*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f4ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafbff')])
    ]))

    story.append(risk_table)
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(llm_content['executive_summary'], body_style))
    story.append(Spacer(1, 0.2*inch))

    # Risk Interpretation
    story.append(Paragraph('WHAT YOUR RISK SCORE MEANS', heading_style))
    story.append(Paragraph(llm_content['risk_interpretation'], body_style))
    story.append(Spacer(1, 0.2*inch))

    # Key Findings
    story.append(Paragraph('KEY FINDINGS', heading_style))
    for finding in llm_content['key_findings']:
        story.append(Paragraph(f'• {finding}', bullet_style))
    story.append(Spacer(1, 0.2*inch))

    # Risk Factors Identified
    if llm_content.get('risk_factors_identified'):
        story.append(Paragraph('RISK FACTORS IDENTIFIED', heading_style))
        for factor in llm_content['risk_factors_identified']:
            story.append(Paragraph(f'• {factor}', bullet_style))
        story.append(Spacer(1, 0.2*inch))

    # Analysis Summaries
    story.append(Paragraph('RETINAL ANALYSIS', heading_style))
    story.append(Paragraph(llm_content['retinal_analysis_summary'], body_style))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph('LIFESTYLE ANALYSIS', heading_style))
    story.append(Paragraph(llm_content['lifestyle_analysis_summary'], body_style))
    story.append(Spacer(1, 0.2*inch))

    # Page Break before recommendations
    story.append(PageBreak())

    # Personalized Recommendations
    story.append(Paragraph('PERSONALIZED ACTION PLAN', heading_style))

    recs = llm_content['personalized_recommendations']

    story.append(Paragraph('Immediate Actions (Next 2 Weeks):', subheading_style))
    for action in recs['immediate_actions']:
        story.append(Paragraph(f'✓ {action}', bullet_style))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph('Short-Term Goals (Next 3 Months):', subheading_style))
    for goal in recs['short_term_goals']:
        story.append(Paragraph(f'→ {goal}', bullet_style))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph('Long-Term Strategy (6-12 Months):', subheading_style))
    for strategy in recs['long_term_strategy']:
        story.append(Paragraph(f'⚡ {strategy}', bullet_style))
    story.append(Spacer(1, 0.2*inch))

    # Intervention Impact Timeline
    story.append(Paragraph('RISK PROGRESSION SCENARIOS', heading_style))

    impact = llm_content['intervention_impact']

    story.append(Paragraph('<b>Without Intervention:</b>', subheading_style))
    story.append(Paragraph(f"• 6 months: {impact['without_intervention']['6_months']}", bullet_style))
    story.append(Paragraph(f"• 12 months: {impact['without_intervention']['12_months']}", bullet_style))
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph('<b>With Lifestyle Intervention:</b>', subheading_style))
    story.append(Paragraph(f"• 3 months: {impact['with_intervention']['3_months']}", bullet_style))
    story.append(Paragraph(f"• 6 months: {impact['with_intervention']['6_months']}", bullet_style))
    story.append(Paragraph(f"• 12 months: {impact['with_intervention']['12_months']}", bullet_style))
    story.append(Spacer(1, 0.2*inch))

    # Dietary Guidance
    story.append(PageBreak())
    story.append(Paragraph('DIETARY GUIDANCE', heading_style))
    for guidance in llm_content['specific_dietary_guidance']:
        story.append(Paragraph(f'• {guidance}', bullet_style))
    story.append(Spacer(1, 0.2*inch))

    # Exercise Prescription
    story.append(Paragraph('EXERCISE PRESCRIPTION', heading_style))
    for exercise in llm_content['exercise_prescription']:
        story.append(Paragraph(f'• {exercise}', bullet_style))
    story.append(Spacer(1, 0.2*inch))

    # Monitoring Plan
    story.append(Paragraph('HEALTH MONITORING PLAN', heading_style))
    for monitor in llm_content['monitoring_plan']:
        story.append(Paragraph(f'• {monitor}', bullet_style))
    story.append(Spacer(1, 0.2*inch))

    # Warning Signs
    story.append(Paragraph('WARNING SIGNS - SEEK IMMEDIATE MEDICAL ATTENTION', heading_style))
    for warning in llm_content['warning_signs']:
        story.append(Paragraph(f'⚠ {warning}', bullet_style))
    story.append(Spacer(1, 0.2*inch))

    # Success Stories & Motivation
    if llm_content.get('success_stories'):
        story.append(Paragraph('YOU CAN DO THIS', heading_style))
        story.append(Paragraph(llm_content['success_stories'], body_style))
        story.append(Spacer(1, 0.2*inch))

    # Resources
    story.append(Paragraph('HELPFUL RESOURCES', heading_style))
    for resource in llm_content['resources']:
        story.append(Paragraph(f'• {resource}', bullet_style))
    story.append(Spacer(1, 0.3*inch))

    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_JUSTIFY,
        leading=10
    )

    disclaimer_text = """
    <b>MEDICAL DISCLAIMER:</b> This report is generated by an AI-powered analysis system for informational
    and educational purposes only. It does not constitute medical advice, diagnosis, or treatment.
    The risk assessments are statistical predictions based on available data and machine learning models.
    This report should not replace professional medical consultation. Always consult with qualified
    healthcare professionals for personalized medical advice, diagnosis, and treatment. Individual
    results and outcomes may vary. DIAVITA and its operators assume no liability for decisions made
    based on this report.
    """
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    story.append(Spacer(1, 0.1*inch))

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#667eea'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(f'Powered by DIAVITA - AI-Driven Diabetes Prevention | © {datetime.now().year}', footer_style))
    story.append(Paragraph('<i>See Clearly & Live Freely</i>', styles['Normal']))

    # Build PDF
    doc.build(story)
    return buffer
