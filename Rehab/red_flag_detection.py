"""
Red Flag Detection System
Evidence-based clinical warning indicators for immediate medical referral
"""

from datetime import datetime
import pandas as pd

def assess_red_flags(patient_data):
    """
    Comprehensive red flag assessment across multiple body regions
    
    Based on: Clinical guidelines from APTA, JOSPT, and international consensus
    """
    
    red_flags = []
    yellow_flags = []
    
    # General systemic red flags
    red_flags.extend(check_systemic_flags(patient_data))
    
    # Region-specific red flags
    if patient_data.get('region') == 'spine':
        red_flags.extend(check_spinal_red_flags(patient_data))
    elif patient_data.get('region') == 'knee':
        red_flags.extend(check_knee_red_flags(patient_data))
    elif patient_data.get('region') == 'shoulder':
        red_flags.extend(check_shoulder_red_flags(patient_data))
    elif patient_data.get('region') == 'ankle':
        red_flags.extend(check_ankle_red_flags(patient_data))
    
    # Psychosocial yellow flags
    yellow_flags.extend(check_psychosocial_flags(patient_data))
    
    # Determine overall risk level
    risk_level = determine_risk_level(red_flags, yellow_flags)
    
    return {
        'red_flags': red_flags,
        'yellow_flags': yellow_flags,
        'risk_level': risk_level,
        'immediate_referral_needed': len(red_flags) > 0,
        'recommendations': generate_recommendations(red_flags, yellow_flags, risk_level),
        'assessment_date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

def check_systemic_flags(data):
    """Check for systemic red flags requiring immediate medical attention"""
    
    flags = []
    
    # Age-related flags
    age = data.get('age', 0)
    if age > 50 and data.get('new_onset_pain', False):
        flags.append({
            'category': 'Age-related',
            'flag': 'New onset pain >50 years',
            'severity': 'High',
            'action': 'Rule out malignancy, fracture',
            'evidence': 'Deyo RA, et al. Ann Intern Med. 1992'
        })
    
    if age < 20 and data.get('progressive_pain', False):
        flags.append({
            'category': 'Age-related',
            'flag': 'Progressive pain <20 years',
            'severity': 'High',
            'action': 'Rule out infection, tumor',
            'evidence': 'Clinical guidelines'
        })
    
    # Constitutional symptoms
    if data.get('fever', False):
        flags.append({
            'category': 'Constitutional',
            'flag': 'Fever with musculoskeletal pain',
            'severity': 'High',
            'action': 'Immediate medical evaluation - infection',
            'evidence': 'Emergency medicine guidelines'
        })
    
    if data.get('unexplained_weight_loss', False):
        flags.append({
            'category': 'Constitutional',
            'flag': 'Unexplained weight loss >10lbs',
            'severity': 'High',
            'action': 'Rule out malignancy',
            'evidence': 'Cancer screening guidelines'
        })
    
    if data.get('night_sweats', False):
        flags.append({
            'category': 'Constitutional',
            'flag': 'Night sweats with pain',
            'severity': 'Medium',
            'action': 'Medical evaluation - systemic disease',
            'evidence': 'Clinical red flag studies'
        })
    
    # Pain characteristics
    if data.get('constant_progressive_pain', False):
        flags.append({
            'category': 'Pain Pattern',
            'flag': 'Constant, progressive, non-mechanical pain',
            'severity': 'High',
            'action': 'Rule out serious pathology',
            'evidence': 'Waddell G. Spine. 1998'
        })
    
    if data.get('night_pain_no_relief', False):
        flags.append({
            'category': 'Pain Pattern',
            'flag': 'Severe night pain, no relief with rest',
            'severity': 'High',
            'action': 'Rule out tumor, infection',
            'evidence': 'Clinical diagnostic guidelines'
        })
    
    return flags

def check_spinal_red_flags(data):
    """Spine-specific red flags"""
    
    flags = []
    
    # Cauda equina syndrome
    if data.get('bladder_dysfunction', False) or data.get('bowel_dysfunction', False):
        flags.append({
            'category': 'Neurological Emergency',
            'flag': 'Bladder/bowel dysfunction',
            'severity': 'EMERGENCY',
            'action': 'IMMEDIATE emergency referral - Cauda equina',
            'evidence': 'Spine emergency protocols'
        })
    
    if data.get('saddle_anesthesia', False):
        flags.append({
            'category': 'Neurological Emergency',
            'flag': 'Saddle anesthesia',
            'severity': 'EMERGENCY',
            'action': 'IMMEDIATE emergency referral - Cauda equina',
            'evidence': 'Neurological emergency guidelines'
        })
    
    # Progressive neurological deficit
    if data.get('progressive_weakness', False):
        flags.append({
            'category': 'Neurological',
            'flag': 'Progressive neurological weakness',
            'severity': 'High',
            'action': 'Urgent neurological evaluation',
            'evidence': 'Clinical neurology guidelines'
        })
    
    # Trauma history
    if data.get('significant_trauma', False):
        flags.append({
            'category': 'Trauma',
            'flag': 'History of significant trauma',
            'severity': 'High',
            'action': 'Rule out fracture - imaging needed',
            'evidence': 'Trauma assessment protocols'
        })
    
    return flags

def check_knee_red_flags(data):
    """Knee-specific red flags"""
    
    flags = []
    
    # Infection signs
    if data.get('joint_effusion', False) and data.get('fever', False):
        flags.append({
            'category': 'Infection',
            'flag': 'Joint effusion with fever',
            'severity': 'High',
            'action': 'Rule out septic arthritis',
            'evidence': 'Orthopedic infection guidelines'
        })
    
    # Vascular compromise
    if data.get('pulse_deficit', False) or data.get('cold_limb', False):
        flags.append({
            'category': 'Vascular',
            'flag': 'Vascular compromise signs',
            'severity': 'EMERGENCY',
            'action': 'IMMEDIATE vascular surgery referral',
            'evidence': 'Vascular emergency protocols'
        })
    
    # Fracture indicators
    if data.get('ottawa_knee_positive', False):
        flags.append({
            'category': 'Fracture',
            'flag': 'Ottawa Knee Rule positive',
            'severity': 'High',
            'action': 'X-ray indicated',
            'evidence': 'Stiell IG, et al. JAMA. 1997'
        })
    
    return flags

def check_shoulder_red_flags(data):
    """Shoulder-specific red flags"""
    
    flags = []
    
    # Vascular compromise
    if data.get('absent_pulse', False):
        flags.append({
            'category': 'Vascular',
            'flag': 'Absent or diminished pulse',
            'severity': 'EMERGENCY',
            'action': 'IMMEDIATE vascular evaluation',
            'evidence': 'Vascular emergency guidelines'
        })
    
    # Neurological compromise
    if data.get('brachial_plexus_signs', False):
        flags.append({
            'category': 'Neurological',
            'flag': 'Brachial plexus compromise',
            'severity': 'High',
            'action': 'Urgent neurological evaluation',
            'evidence': 'Neurological assessment guidelines'
        })
    
    return flags

def check_ankle_red_flags(data):
    """Ankle-specific red flags"""
    
    flags = []
    
    # Ottawa Ankle Rules
    if data.get('ottawa_ankle_positive', False):
        flags.append({
            'category': 'Fracture',
            'flag': 'Ottawa Ankle Rule positive',
            'severity': 'High',
            'action': 'X-ray indicated',
            'evidence': 'Stiell IG, et al. Ann Emerg Med. 1992'
        })
    
    # Compartment syndrome
    if data.get('severe_swelling', False) and data.get('severe_pain', False):
        flags.append({
            'category': 'Compartment Syndrome',
            'flag': 'Severe pain with passive stretch',
            'severity': 'EMERGENCY',
            'action': 'IMMEDIATE surgical evaluation',
            'evidence': 'Orthopedic emergency protocols'
        })
    
    return flags

def check_psychosocial_flags(data):
    """Psychosocial yellow flags affecting recovery"""
    
    flags = []
    
    # Work-related factors
    if data.get('job_dissatisfaction', False):
        flags.append({
            'category': 'Occupational',
            'flag': 'High job dissatisfaction',
            'impact': 'Delayed recovery',
            'intervention': 'Address work-related concerns'
        })
    
    # Psychological factors
    if data.get('depression_screening_positive', False):
        flags.append({
            'category': 'Psychological',
            'flag': 'Depression screening positive',
            'impact': 'Poor treatment outcomes',
            'intervention': 'Consider psychological support'
        })
    
    if data.get('fear_avoidance_high', False):
        flags.append({
            'category': 'Psychological',
            'flag': 'High fear-avoidance beliefs',
            'impact': 'Chronic disability risk',
            'intervention': 'Cognitive-behavioral approach'
        })
    
    # Social factors
    if data.get('poor_social_support', False):
        flags.append({
            'category': 'Social',
            'flag': 'Poor social support',
            'impact': 'Slower recovery',
            'intervention': 'Enhance support systems'
        })
    
    return flags

def determine_risk_level(red_flags, yellow_flags):
    """Determine overall risk level"""
    
    emergency_flags = [f for f in red_flags if f.get('severity') == 'EMERGENCY']
    high_flags = [f for f in red_flags if f.get('severity') == 'High']
    
    if emergency_flags:
        return 'EMERGENCY'
    elif len(high_flags) >= 2:
        return 'HIGH'
    elif len(high_flags) >= 1:
        return 'MODERATE'
    elif len(yellow_flags) >= 3:
        return 'MODERATE'
    elif len(yellow_flags) >= 1:
        return 'LOW'
    else:
        return 'MINIMAL'

def generate_recommendations(red_flags, yellow_flags, risk_level):
    """Generate specific recommendations based on flags"""
    
    recommendations = []
    
    if risk_level == 'EMERGENCY':
        recommendations.append({
            'priority': 'IMMEDIATE',
            'action': 'Emergency medical referral',
            'timeframe': 'Within hours',
            'rationale': 'Life or limb-threatening condition possible'
        })
    
    elif risk_level == 'HIGH':
        recommendations.append({
            'priority': 'URGENT',
            'action': 'Medical evaluation within 24-48 hours',
            'timeframe': '1-2 days',
            'rationale': 'Serious pathology needs ruling out'
        })
    
    elif risk_level == 'MODERATE':
        recommendations.append({
            'priority': 'ROUTINE',
            'action': 'Medical consultation recommended',
            'timeframe': '1-2 weeks',
            'rationale': 'Monitor for progression, address yellow flags'
        })
    
    # Specific recommendations for yellow flags
    if yellow_flags:
        recommendations.append({
            'priority': 'PREVENTIVE',
            'action': 'Address psychosocial factors',
            'timeframe': 'Ongoing',
            'rationale': 'Optimize recovery potential'
        })
    
    return recommendations

def create_red_flag_screening_form():
    """Create a systematic screening questionnaire"""
    
    screening_questions = {
        'general': [
            {'question': 'Age over 50 with new onset pain?', 'key': 'new_onset_pain'},
            {'question': 'Fever or recent infection?', 'key': 'fever'},
            {'question': 'Unexplained weight loss >10lbs?', 'key': 'unexplained_weight_loss'},
            {'question': 'Constant, progressive pain?', 'key': 'constant_progressive_pain'},
            {'question': 'Severe night pain, no relief?', 'key': 'night_pain_no_relief'}
        ],
        'neurological': [
            {'question': 'Bladder or bowel dysfunction?', 'key': 'bladder_dysfunction'},
            {'question': 'Saddle numbness?', 'key': 'saddle_anesthesia'},
            {'question': 'Progressive weakness?', 'key': 'progressive_weakness'},
            {'question': 'Numbness in hands/feet?', 'key': 'peripheral_numbness'}
        ],
        'trauma': [
            {'question': 'Significant recent trauma?', 'key': 'significant_trauma'},
            {'question': 'Unable to bear weight?', 'key': 'unable_bear_weight'}
        ],
        'psychosocial': [
            {'question': 'High job dissatisfaction?', 'key': 'job_dissatisfaction'},
            {'question': 'Feeling depressed?', 'key': 'depression_screening_positive'},
            {'question': 'Afraid movement will cause harm?', 'key': 'fear_avoidance_high'}
        ]
    }
    
    return screening_questions