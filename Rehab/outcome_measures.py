"""
Evidence-Based Outcome Measure Calculators
Scientifically validated assessment tools for rehabilitation
"""

import pandas as pd
from datetime import datetime

def calculate_ikdc_score(responses):
    """
    Calculate IKDC (International Knee Documentation Committee) Score
    
    Based on: Irrgang JJ, et al. Am J Sports Med. 2001;29(5):600-613.
    
    Args:
        responses (dict): Dictionary with question responses
        
    Returns:
        dict: Contains score, interpretation, and recommendations
    """
    
    # IKDC Scoring weights (simplified version - key questions)
    questions = {
        'pain_level': {'weight': 10, 'reverse': True},  # 0=severe, 10=none
        'swelling': {'weight': 5, 'reverse': True},     # 0=severe, 4=none  
        'locking': {'weight': 5, 'reverse': True},      # 0=constant, 4=never
        'instability': {'weight': 10, 'reverse': True}, # 0=constant, 4=never
        'activity_level': {'weight': 10, 'reverse': False}, # 0=unable, 4=normal
        'function_score': {'weight': 15, 'reverse': False}, # 0=cannot do, 4=no difficulty
        'sports_participation': {'weight': 5, 'reverse': False} # 0=unable, 4=normal
    }
    
    total_score = 0
    max_possible = 0
    
    for question, config in questions.items():
        if question in responses:
            value = responses[question]
            weight = config['weight']
            
            if config['reverse']:
                # Higher values = better (reverse scoring)
                score = value * weight
            else:
                # Lower values = better (normal scoring)  
                score = value * weight
                
            total_score += score
            max_possible += 4 * weight  # Max response = 4
    
    # Convert to percentage
    ikdc_score = (total_score / max_possible) * 100 if max_possible > 0 else 0
    
    # Clinical interpretation based on research
    if ikdc_score >= 90:
        interpretation = "Excellent function"
        recommendation = "Consider return to high-level activities"
        risk_level = "Low"
    elif ikdc_score >= 80:
        interpretation = "Good function"
        recommendation = "Continue strengthening, monitor for improvements"
        risk_level = "Low-Moderate"
    elif ikdc_score >= 70:
        interpretation = "Fair function"
        recommendation = "Focus on functional training and symptom management"
        risk_level = "Moderate"
    elif ikdc_score >= 60:
        interpretation = "Poor function"
        recommendation = "Comprehensive rehabilitation needed"
        risk_level = "High"
    else:
        interpretation = "Very poor function"
        recommendation = "Consider medical evaluation and intensive rehabilitation"
        risk_level = "Very High"
    
    return {
        'score': round(ikdc_score, 1),
        'interpretation': interpretation,
        'recommendation': recommendation,
        'risk_level': risk_level,
        'date_assessed': datetime.now().strftime('%Y-%m-%d'),
        'mcid': 9.0,  # Minimal Clinically Important Difference
        'score_change_needed': max(0, round(9.0 - (ikdc_score - 60), 1)) if ikdc_score < 69 else 0
    }

def calculate_koos_score(responses):
    """
    Calculate KOOS (Knee Injury and Osteoarthritis Outcome Score)
    
    Based on: Roos EM, et al. J Orthop Sports Phys Ther. 1998;28(2):88-96.
    """
    
    subscales = {
        'pain': {
            'questions': ['pain_walking', 'pain_stairs', 'pain_bed', 'pain_sitting', 'pain_standing'],
            'weight': 1.0
        },
        'symptoms': {
            'questions': ['swelling', 'grinding', 'catching', 'stiffness', 'range_motion'],
            'weight': 1.0
        },
        'adl': {  # Activities of Daily Living
            'questions': ['stairs_descend', 'stairs_ascend', 'rising_bed', 'rising_sitting', 'standing'],
            'weight': 1.2
        },
        'sport': {
            'questions': ['squatting', 'running', 'jumping', 'cutting', 'kneeling'],
            'weight': 1.5
        },
        'qol': {  # Quality of Life
            'questions': ['aware_problem', 'lifestyle_modification', 'confidence', 'difficulty_general'],
            'weight': 2.0
        }
    }
    
    subscale_scores = {}
    
    for subscale, config in subscales.items():
        total = 0
        count = 0
        
        for question in config['questions']:
            if question in responses:
                # KOOS uses 0-4 scale where 0=no problems, 4=extreme problems
                # Convert to 0-100 where 100=no problems
                value = responses[question]
                normalized = (4 - value) * 25  # Convert to 0-100 scale
                total += normalized
                count += 1
        
        if count > 0:
            subscale_scores[subscale] = round(total / count, 1)
        else:
            subscale_scores[subscale] = 0
    
    # Overall KOOS score (weighted average)
    total_weighted = 0
    total_weights = 0
    
    for subscale, score in subscale_scores.items():
        weight = subscales[subscale]['weight']
        total_weighted += score * weight
        total_weights += weight
    
    overall_score = round(total_weighted / total_weights, 1) if total_weights > 0 else 0
    
    # Clinical interpretation
    if overall_score >= 85:
        interpretation = "Minimal knee problems"
        recommendation = "Maintain current activity level"
    elif overall_score >= 70:
        interpretation = "Mild knee problems"
        recommendation = "Monitor symptoms, continue strengthening"
    elif overall_score >= 55:
        interpretation = "Moderate knee problems"
        recommendation = "Focused rehabilitation needed"
    else:
        interpretation = "Severe knee problems"
        recommendation = "Comprehensive treatment and possible medical evaluation"
    
    return {
        'overall_score': overall_score,
        'subscale_scores': subscale_scores,
        'interpretation': interpretation,
        'recommendation': recommendation,
        'date_assessed': datetime.now().strftime('%Y-%m-%d'),
        'mcid': 8.0  # Minimal Clinically Important Difference
    }

def calculate_dash_score(responses):
    """
    Calculate DASH (Disabilities of Arm, Shoulder, and Hand) Score
    
    Based on: Hudak PL, et al. Am J Ind Med. 1996;29(6):602-8.
    """
    
    # DASH questions (simplified key questions)
    questions = [
        'open_jar', 'write', 'turn_key', 'prepare_meal', 'push_door',
        'place_object_shelf', 'heavy_chores', 'garden', 'make_bed',
        'carry_bag', 'carry_heavy', 'pain', 'activity_pain',
        'tingling', 'weakness', 'stiffness', 'sleep_difficulty',
        'work_difficulty', 'recreation_difficulty', 'social_limitation'
    ]
    
    total_score = 0
    answered_questions = 0
    
    for question in questions:
        if question in responses:
            # DASH uses 1-5 scale where 1=no difficulty, 5=unable
            value = responses[question]
            total_score += value
            answered_questions += 1
    
    if answered_questions < 18:  # Need at least 18/30 questions answered
        return {
            'error': 'Insufficient responses',
            'message': 'At least 18 questions must be answered for valid DASH score'
        }
    
    # Calculate DASH score: ((sum of responses/number of responses) - 1) * 25
    dash_score = ((total_score / answered_questions) - 1) * 25
    dash_score = round(dash_score, 1)
    
    # Clinical interpretation
    if dash_score <= 15:
        interpretation = "Minimal disability"
        recommendation = "Maintain current function"
    elif dash_score <= 30:
        interpretation = "Mild disability"
        recommendation = "Monitor symptoms, consider preventive exercises"
    elif dash_score <= 50:
        interpretation = "Moderate disability"
        recommendation = "Rehabilitation and activity modification needed"
    else:
        interpretation = "Severe disability"
        recommendation = "Comprehensive treatment required"
    
    return {
        'score': dash_score,
        'interpretation': interpretation,
        'recommendation': recommendation,
        'date_assessed': datetime.now().strftime('%Y-%m-%d'),
        'mcid': 10.0,  # Minimal Clinically Important Difference
        'questions_answered': answered_questions
    }

def calculate_nprs_score(current_pain, worst_pain, least_pain, average_pain):
    """
    Calculate Numeric Pain Rating Scale (NPRS) composite score
    
    Based on: Jensen MP, et al. Pain. 2003;102(1-2):79-85.
    """
    
    scores = [current_pain, worst_pain, least_pain, average_pain]
    valid_scores = [s for s in scores if s is not None]
    
    if len(valid_scores) < 3:
        return {
            'error': 'Insufficient data',
            'message': 'At least 3 pain ratings required'
        }
    
    composite_score = sum(valid_scores) / len(valid_scores)
    
    # Clinical interpretation
    if composite_score <= 3:
        interpretation = "Mild pain"
        impact = "Minimal functional impact"
        recommendation = "Continue current activities, monitor"
    elif composite_score <= 6:
        interpretation = "Moderate pain"
        impact = "Some functional limitations"
        recommendation = "Pain management strategies and activity modification"
    else:
        interpretation = "Severe pain"
        impact = "Significant functional impairment"
        recommendation = "Comprehensive pain management and medical evaluation"
    
    return {
        'composite_score': round(composite_score, 1),
        'individual_scores': {
            'current': current_pain,
            'worst': worst_pain,
            'least': least_pain,
            'average': average_pain
        },
        'interpretation': interpretation,
        'functional_impact': impact,
        'recommendation': recommendation,
        'date_assessed': datetime.now().strftime('%Y-%m-%d'),
        'mcid': 2.0  # Minimal Clinically Important Difference
    }

def track_outcome_changes(previous_scores, current_scores, measure_type):
    """
    Track changes in outcome measures over time
    """
    
    if not previous_scores or measure_type not in previous_scores:
        return {
            'change': 0,
            'clinically_significant': False,
            'trend': 'baseline',
            'message': 'Baseline assessment - no previous scores to compare'
        }
    
    # Get MCID for the measure
    mcid_values = {
        'ikdc': 9.0,
        'koos': 8.0,
        'dash': 10.0,
        'nprs': 2.0
    }
    
    mcid = mcid_values.get(measure_type, 5.0)
    
    if measure_type == 'nprs':
        # For pain, lower is better
        change = previous_scores[measure_type] - current_scores
        improvement = change > 0
    else:
        # For function scores, higher is better
        change = current_scores - previous_scores[measure_type]
        improvement = change > 0
    
    clinically_significant = abs(change) >= mcid
    
    if improvement and clinically_significant:
        trend = 'significant_improvement'
        message = f"Clinically significant improvement ({abs(change):.1f} points, MCID: {mcid})"
    elif improvement:
        trend = 'improvement'
        message = f"Improvement noted ({abs(change):.1f} points), approaching clinical significance"
    elif not improvement and clinically_significant:
        trend = 'significant_decline'
        message = f"Clinically significant decline ({abs(change):.1f} points)"
    elif not improvement:
        trend = 'decline'
        message = f"Slight decline noted ({abs(change):.1f} points)"
    else:
        trend = 'stable'
        message = "Scores remain stable"
    
    return {
        'change': round(change, 1),
        'clinically_significant': clinically_significant,
        'trend': trend,
        'message': message,
        'mcid': mcid
    }