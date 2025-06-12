"""
Recovery Timeline Prediction Models
Evidence-based algorithms for predicting rehabilitation timelines
"""

import math
from datetime import datetime, timedelta
import pandas as pd

def predict_recovery_timeline(injury_data, patient_factors, treatment_factors):
    """
    Predict recovery timeline using evidence-based factors
    
    Based on: van der Horst N, et al. Sports Med. 2015;45(7):1063-1075.
              Ardern CL, et al. Am J Sports Med. 2014;42(5):1247-1255.
    """
    
    # Base recovery times (in weeks) from literature
    base_recovery_times = {
        "ACL": {
            "conservative": 16,
            "surgical": 24,
            "return_to_sport": 32
        },
        "Achilles": {
            "conservative": 12,
            "surgical": 20,
            "return_to_sport": 28
        },
        "Hamstring": {
            "grade_1": 3,
            "grade_2": 6,
            "grade_3": 12,
            "return_to_sport": 16
        },
        "Meniscus": {
            "conservative": 8,
            "repair": 16,
            "partial_removal": 12
        },
        "Rotator_Cuff": {
            "conservative": 12,
            "surgical": 20,
            "return_to_sport": 24
        },
        "Ankle_Sprain": {
            "grade_1": 2,
            "grade_2": 4,
            "grade_3": 8
        }
    }
    
    injury_type = injury_data.get("injury_type", "ACL")
    injury_severity = injury_data.get("severity", "conservative")
    treatment_type = injury_data.get("treatment", "conservative")
    
    # Get base timeline
    injury_timelines = base_recovery_times.get(injury_type, base_recovery_times["ACL"])
    
    if treatment_type in injury_timelines:
        base_weeks = injury_timelines[treatment_type]
    elif injury_severity in injury_timelines:
        base_weeks = injury_timelines[injury_severity]
    else:
        base_weeks = injury_timelines.get("conservative", 12)
    
    # Calculate modifying factors
    modifiers = calculate_recovery_modifiers(patient_factors, treatment_factors, injury_data)
    
    # Apply modifiers to base timeline
    adjusted_weeks = base_weeks * modifiers["total_modifier"]
    
    # Calculate phase timelines
    phase_distribution = get_phase_distribution(injury_type, treatment_type)
    
    phase_timelines = {}
    cumulative_weeks = 0
    
    for phase, percentage in phase_distribution.items():
        phase_weeks = adjusted_weeks * percentage
        phase_timelines[phase] = {
            "duration_weeks": round(phase_weeks, 1),
            "start_week": round(cumulative_weeks, 1),
            "end_week": round(cumulative_weeks + phase_weeks, 1)
        }
        cumulative_weeks += phase_weeks
    
    # Calculate milestone dates
    start_date = datetime.strptime(injury_data.get("injury_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
    milestones = calculate_milestone_dates(start_date, phase_timelines)
    
    # Confidence intervals
    confidence_intervals = calculate_confidence_intervals(adjusted_weeks, modifiers)
    
    return {
        "total_recovery_weeks": round(adjusted_weeks, 1),
        "base_recovery_weeks": base_weeks,
        "modifying_factors": modifiers,
        "phase_timelines": phase_timelines,
        "milestone_dates": milestones,
        "confidence_intervals": confidence_intervals,
        "prediction_accuracy": calculate_prediction_accuracy(modifiers),
        "injury_info": {
            "type": injury_type,
            "severity": injury_severity,
            "treatment": treatment_type
        }
    }

def calculate_recovery_modifiers(patient_factors, treatment_factors, injury_data):
    """Calculate factors that modify recovery timeline"""
    
    modifiers = {
        "age_modifier": 1.0,
        "fitness_modifier": 1.0,
        "compliance_modifier": 1.0,
        "comorbidity_modifier": 1.0,
        "treatment_modifier": 1.0,
        "psychological_modifier": 1.0,
        "injury_specific_modifier": 1.0
    }
    
    # Age factor (based on tissue healing research)
    age = patient_factors.get("age", 30)
    if age < 20:
        modifiers["age_modifier"] = 0.85  # Faster healing
    elif age < 30:
        modifiers["age_modifier"] = 0.95
    elif age < 40:
        modifiers["age_modifier"] = 1.0
    elif age < 50:
        modifiers["age_modifier"] = 1.15
    else:
        modifiers["age_modifier"] = 1.3  # Slower healing
    
    # Fitness level
    fitness_level = patient_factors.get("fitness_level", "average")
    fitness_modifiers = {
        "elite": 0.8,
        "high": 0.9,
        "average": 1.0,
        "low": 1.2,
        "sedentary": 1.4
    }
    modifiers["fitness_modifier"] = fitness_modifiers.get(fitness_level, 1.0)
    
    # Compliance factor
    compliance = patient_factors.get("expected_compliance", "good")
    compliance_modifiers = {
        "excellent": 0.85,
        "good": 1.0,
        "fair": 1.25,
        "poor": 1.6
    }
    modifiers["compliance_modifier"] = compliance_modifiers.get(compliance, 1.0)
    
    # Comorbidities
    comorbidities = patient_factors.get("comorbidities", [])
    comorbidity_impact = {
        "diabetes": 1.3,
        "smoking": 1.4,
        "obesity": 1.2,
        "cardiovascular": 1.15,
        "autoimmune": 1.25
    }
    
    comorbidity_modifier = 1.0
    for condition in comorbidities:
        if condition in comorbidity_impact:
            comorbidity_modifier *= comorbidity_impact[condition]
    
    modifiers["comorbidity_modifier"] = min(comorbidity_modifier, 2.0)  # Cap at 2x
    
    # Treatment quality
    treatment_quality = treatment_factors.get("treatment_quality", "standard")
    treatment_modifiers = {
        "optimal": 0.9,
        "good": 0.95,
        "standard": 1.0,
        "suboptimal": 1.2,
        "poor": 1.4
    }
    modifiers["treatment_modifier"] = treatment_modifiers.get(treatment_quality, 1.0)
    
    # Psychological factors
    psychological_score = patient_factors.get("psychological_readiness", 70)  # 0-100
    if psychological_score >= 80:
        modifiers["psychological_modifier"] = 0.95
    elif psychological_score >= 60:
        modifiers["psychological_modifier"] = 1.0
    elif psychological_score >= 40:
        modifiers["psychological_modifier"] = 1.15
    else:
        modifiers["psychological_modifier"] = 1.3
    
    # Injury-specific factors
    injury_specific = calculate_injury_specific_modifiers(injury_data)
    modifiers["injury_specific_modifier"] = injury_specific
    
    # Calculate total modifier
    total_modifier = 1.0
    for modifier_value in modifiers.values():
        if modifier_value != modifiers.get("total_modifier", 1.0):  # Exclude total_modifier from calculation
            total_modifier *= modifier_value
    
    modifiers["total_modifier"] = total_modifier
    
    return modifiers

def calculate_injury_specific_modifiers(injury_data):
    """Calculate injury-specific modifying factors"""
    
    injury_type = injury_data.get("injury_type", "ACL")
    
    modifier = 1.0
    
    if injury_type == "ACL":
        # Graft type affects timeline
        graft_type = injury_data.get("graft_type", "hamstring")
        if graft_type == "patellar_tendon":
            modifier *= 1.1  # Slightly longer due to donor site
        elif graft_type == "allograft":
            modifier *= 0.95  # No donor site morbidity
        
        # Meniscus involvement
        if injury_data.get("meniscus_tear", False):
            modifier *= 1.2
    
    elif injury_type == "Hamstring":
        # Location affects healing
        location = injury_data.get("location", "muscle_belly")
        if location == "proximal_tendon":
            modifier *= 1.4  # Slower healing
        elif location == "distal_tendon":
            modifier *= 1.2
        
        # MRI grade
        mri_grade = injury_data.get("mri_grade", 2)
        if mri_grade == 1:
            modifier *= 0.7
        elif mri_grade == 3:
            modifier *= 1.5
    
    elif injury_type == "Achilles":
        # Rupture vs tendinopathy
        pathology = injury_data.get("pathology", "tendinopathy")
        if pathology == "rupture":
            modifier *= 1.6
        
        # Location of pathology
        location = injury_data.get("location", "mid_portion")
        if location == "insertional":
            modifier *= 1.3  # More complex healing
    
    return modifier

def get_phase_distribution(injury_type, treatment_type):
    """Get typical phase distribution for different injuries"""
    
    phase_distributions = {
        "ACL": {
            "surgical": {
                "early": 0.25,      # Weeks 0-6
                "mid": 0.35,        # Weeks 6-14
                "late": 0.25,       # Weeks 14-22
                "return_to_sport": 0.15  # Weeks 22-24
            },
            "conservative": {
                "early": 0.3,
                "mid": 0.4,
                "late": 0.3,
                "return_to_sport": 0.0
            }
        },
        "Hamstring": {
            "grade_1": {
                "early": 0.4,
                "mid": 0.6,
                "late": 0.0,
                "return_to_sport": 0.0
            },
            "grade_2": {
                "early": 0.3,
                "mid": 0.5,
                "late": 0.2,
                "return_to_sport": 0.0
            },
            "grade_3": {
                "early": 0.25,
                "mid": 0.4,
                "late": 0.25,
                "return_to_sport": 0.1
            }
        },
        "Achilles": {
            "conservative": {
                "early": 0.35,
                "mid": 0.45,
                "late": 0.2,
                "return_to_sport": 0.0
            },
            "surgical": {
                "early": 0.3,
                "mid": 0.4,
                "late": 0.2,
                "return_to_sport": 0.1
            }
        }
    }
    
    # Default distribution
    default_distribution = {
        "early": 0.3,
        "mid": 0.4,
        "late": 0.2,
        "return_to_sport": 0.1
    }
    
    injury_phases = phase_distributions.get(injury_type, {})
    return injury_phases.get(treatment_type, default_distribution)

def calculate_milestone_dates(start_date, phase_timelines):
    """Calculate key milestone dates"""
    
    milestones = {}
    
    for phase, timeline in phase_timelines.items():
        start_milestone = start_date + timedelta(weeks=timeline["start_week"])
        end_milestone = start_date + timedelta(weeks=timeline["end_week"])
        
        milestones[f"{phase}_start"] = start_milestone.strftime("%Y-%m-%d")
        milestones[f"{phase}_end"] = end_milestone.strftime("%Y-%m-%d")
    
    # Key clinical milestones
    milestones["pain_free_date"] = (start_date + timedelta(weeks=phase_timelines["early"]["duration_weeks"] * 0.6)).strftime("%Y-%m-%d")
    milestones["full_rom_date"] = (start_date + timedelta(weeks=phase_timelines["early"]["duration_weeks"] * 0.8)).strftime("%Y-%m-%d")
    milestones["running_clearance"] = (start_date + timedelta(weeks=phase_timelines["mid"]["end_week"] * 0.8)).strftime("%Y-%m-%d")
    
    if "return_to_sport" in phase_timelines:
        milestones["rts_testing_date"] = (start_date + timedelta(weeks=phase_timelines["late"]["end_week"])).strftime("%Y-%m-%d")
        milestones["full_rts_date"] = (start_date + timedelta(weeks=phase_timelines["return_to_sport"]["end_week"])).strftime("%Y-%m-%d")
    
    return milestones

def calculate_confidence_intervals(predicted_weeks, modifiers):
    """Calculate confidence intervals for predictions"""
    
    # Base uncertainty increases with number of modifying factors
    base_uncertainty = 0.15  # ±15% base uncertainty
    
    # Increase uncertainty based on extreme modifiers
    modifier_uncertainty = 0
    for key, value in modifiers.items():
        if key != "total_modifier":
            if value > 1.2 or value < 0.8:
                modifier_uncertainty += 0.05
    
    total_uncertainty = min(base_uncertainty + modifier_uncertainty, 0.4)  # Cap at 40%
    
    # Calculate intervals
    uncertainty_weeks = predicted_weeks * total_uncertainty
    
    return {
        "95_percent_range": {
            "lower": round(predicted_weeks - 1.96 * uncertainty_weeks, 1),
            "upper": round(predicted_weeks + 1.96 * uncertainty_weeks, 1)
        },
        "80_percent_range": {
            "lower": round(predicted_weeks - 1.28 * uncertainty_weeks, 1),
            "upper": round(predicted_weeks + 1.28 * uncertainty_weeks, 1)
        },
        "uncertainty_percentage": round(total_uncertainty * 100, 1)
    }

def calculate_prediction_accuracy(modifiers):
    """Estimate prediction accuracy based on modifying factors"""
    
    # Start with base accuracy
    base_accuracy = 75  # 75% base accuracy
    
    # Reduce accuracy for each extreme modifier
    accuracy_reduction = 0
    for key, value in modifiers.items():
        if key != "total_modifier":
            if value > 1.3 or value < 0.7:
                accuracy_reduction += 5
            elif value > 1.2 or value < 0.8:
                accuracy_reduction += 2
    
    final_accuracy = max(base_accuracy - accuracy_reduction, 40)  # Minimum 40% accuracy
    
    if final_accuracy >= 80:
        accuracy_level = "High"
    elif final_accuracy >= 70:
        accuracy_level = "Good"
    elif final_accuracy >= 60:
        accuracy_level = "Moderate"
    else:
        accuracy_level = "Low"
    
    return {
        "percentage": final_accuracy,
        "level": accuracy_level,
        "factors_affecting": accuracy_reduction > 10
    }

def generate_timeline_recommendations(prediction_data):
    """Generate recommendations to optimize timeline"""
    
    recommendations = []
    modifiers = prediction_data["modifying_factors"]
    
    # Check for modifiable factors
    if modifiers["compliance_modifier"] > 1.1:
        recommendations.append({
            "category": "Compliance",
            "recommendation": "Enhance patient education and motivation strategies",
            "potential_improvement": "15-25% faster recovery",
            "priority": "High"
        })
    
    if modifiers["fitness_modifier"] > 1.1:
        recommendations.append({
            "category": "Fitness",
            "recommendation": "Pre-rehabilitation conditioning program",
            "potential_improvement": "10-20% faster recovery",
            "priority": "Medium"
        })
    
    if modifiers["treatment_modifier"] > 1.1:
        recommendations.append({
            "category": "Treatment Quality",
            "recommendation": "Optimize treatment protocols and specialist referrals",
            "potential_improvement": "15-30% faster recovery",
            "priority": "High"
        })
    
    if modifiers["psychological_modifier"] > 1.1:
        recommendations.append({
            "category": "Psychological",
            "recommendation": "Address fear-avoidance and psychological barriers",
            "potential_improvement": "10-15% faster recovery",
            "priority": "Medium"
        })
    
    # Modifiable comorbidities
    if modifiers["comorbidity_modifier"] > 1.1:
        recommendations.append({
            "category": "Health Optimization",
            "recommendation": "Address modifiable risk factors (smoking cessation, weight management)",
            "potential_improvement": "20-40% faster recovery",
            "priority": "High"
        })
    
    return recommendations

def track_recovery_progress(prediction_data, actual_progress):
    """Track actual progress against predictions"""
    
    predicted_timeline = prediction_data["phase_timelines"]
    current_date = datetime.now()
    injury_date = datetime.strptime(prediction_data.get("injury_date", "2024-01-01"), "%Y-%m-%d")
    
    weeks_elapsed = (current_date - injury_date).days / 7
    
    # Determine expected vs actual phase
    expected_phase = determine_expected_phase(weeks_elapsed, predicted_timeline)
    actual_phase = actual_progress.get("current_phase", "early")
    
    # Calculate progress metrics
    progress_metrics = {
        "weeks_elapsed": round(weeks_elapsed, 1),
        "expected_phase": expected_phase,
        "actual_phase": actual_phase,
        "on_track": expected_phase == actual_phase,
        "timeline_variance": calculate_timeline_variance(predicted_timeline, actual_progress),
        "completion_percentage": calculate_completion_percentage(weeks_elapsed, prediction_data["total_recovery_weeks"])
    }
    
    return progress_metrics

def determine_expected_phase(weeks_elapsed, predicted_timeline):
    """Determine which phase patient should be in based on elapsed time"""
    
    for phase, timeline in predicted_timeline.items():
        if timeline["start_week"] <= weeks_elapsed <= timeline["end_week"]:
            return phase
    
    return "unknown"

def calculate_timeline_variance(predicted_timeline, actual_progress):
    """Calculate how far off track the patient is"""
    
    # This would integrate with actual progress data
    # For now, return a placeholder structure
    
    return {
        "days_ahead": 0,
        "days_behind": 0,
        "variance_percentage": 0,
        "trend": "on_track"
    }

def calculate_completion_percentage(weeks_elapsed, total_weeks):
    """Calculate what percentage of recovery is complete"""
    
    percentage = min((weeks_elapsed / total_weeks) * 100, 100)
    return round(percentage, 1)