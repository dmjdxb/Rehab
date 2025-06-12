"""
Exercise Contraindication Checking System
Evidence-based safety protocols for exercise prescription
"""

from datetime import datetime
import pandas as pd

def check_exercise_contraindications(patient_profile, exercise_data, injury_data):
    """
    Comprehensive contraindication checking for exercise prescription
    
    Based on: ACSM's Guidelines for Exercise Testing and Prescription. 10th ed.
              Clinical exercise physiology guidelines
    """
    
    contraindications = {
        "absolute": [],
        "relative": [],
        "precautions": [],
        "modifications": []
    }
    
    # Check absolute contraindications
    absolute_checks = check_absolute_contraindications(patient_profile, exercise_data)
    contraindications["absolute"].extend(absolute_checks)
    
    # Check relative contraindications
    relative_checks = check_relative_contraindications(patient_profile, exercise_data, injury_data)
    contraindications["relative"].extend(relative_checks)
    
    # Check exercise-specific precautions
    precaution_checks = check_exercise_precautions(exercise_data, injury_data, patient_profile)
    contraindications["precautions"].extend(precaution_checks)
    
    # Generate modifications
    modifications = generate_exercise_modifications(contraindications, exercise_data, injury_data)
    contraindications["modifications"] = modifications
    
    # Determine overall safety level
    safety_assessment = determine_safety_level(contraindications)
    
    return {
        "contraindications": contraindications,
        "safety_assessment": safety_assessment,
        "exercise_cleared": len(contraindications["absolute"]) == 0,
        "requires_modification": len(contraindications["relative"]) > 0 or len(contraindications["precautions"]) > 0,
        "assessment_date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def check_absolute_contraindications(patient_profile, exercise_data):
    """Check for absolute contraindications that prevent exercise"""
    
    absolute_contraindications = []
    
    # Cardiovascular absolute contraindications
    if patient_profile.get("unstable_angina", False):
        absolute_contraindications.append({
            "category": "Cardiovascular",
            "contraindication": "Unstable angina",
            "severity": "ABSOLUTE",
            "action": "Exercise prohibited until medical clearance",
            "evidence": "ACSM Guidelines 2022"
        })
    
    if patient_profile.get("uncontrolled_arrhythmia", False):
        absolute_contraindications.append({
            "category": "Cardiovascular", 
            "contraindication": "Uncontrolled cardiac arrhythmia",
            "severity": "ABSOLUTE",
            "action": "Cardiology clearance required",
            "evidence": "Exercise physiology guidelines"
        })
    
    # Respiratory absolute contraindications
    if patient_profile.get("severe_pulmonary_edema", False):
        absolute_contraindications.append({
            "category": "Respiratory",
            "contraindication": "Severe pulmonary edema",
            "severity": "ABSOLUTE", 
            "action": "Exercise contraindicated",
            "evidence": "Respiratory medicine guidelines"
        })
    
    # Metabolic absolute contraindications
    blood_glucose = patient_profile.get("blood_glucose", 100)
    if blood_glucose > 300:
        absolute_contraindications.append({
            "category": "Metabolic",
            "contraindication": "Severe hyperglycemia (>300 mg/dL)",
            "severity": "ABSOLUTE",
            "action": "Medical management required before exercise",
            "evidence": "Diabetes exercise guidelines"
        })
    
    # Infection/fever
    if patient_profile.get("fever", False) or patient_profile.get("systemic_infection", False):
        absolute_contraindications.append({
            "category": "Infectious",
            "contraindication": "Fever or systemic infection",
            "severity": "ABSOLUTE",
            "action": "Wait until fever-free for 24 hours",
            "evidence": "Exercise immunology research"
        })
    
    # Exercise-specific absolute contraindications
    exercise_type = exercise_data.get("type", "").lower()
    exercise_intensity = exercise_data.get("intensity", "moderate")
    
    if exercise_intensity == "high" and patient_profile.get("recent_cardiac_event", False):
        absolute_contraindications.append({
            "category": "Exercise-Specific",
            "contraindication": "High-intensity exercise post-cardiac event",
            "severity": "ABSOLUTE",
            "action": "Reduce to low-moderate intensity",
            "evidence": "Cardiac rehabilitation guidelines"
        })
    
    return absolute_contraindications

def check_relative_contraindications(patient_profile, exercise_data, injury_data):
    """Check for relative contraindications requiring caution"""
    
    relative_contraindications = []
    
    # Age-related considerations
    age = patient_profile.get("age", 30)
    if age > 65 and exercise_data.get("intensity", "moderate") == "high":
        relative_contraindications.append({
            "category": "Age-Related",
            "contraindication": "High-intensity exercise in older adults",
            "severity": "RELATIVE",
            "recommendation": "Progressive intensity increase with monitoring",
            "evidence": "Geriatric exercise guidelines"
        })
    
    # Cardiovascular relative contraindications
    systolic_bp = patient_profile.get("systolic_bp", 120)
    if systolic_bp > 180:
        relative_contraindications.append({
            "category": "Cardiovascular",
            "contraindication": "Severe hypertension (SBP >180)",
            "severity": "RELATIVE", 
            "recommendation": "Lower intensity, avoid Valsalva maneuvers",
            "evidence": "Hypertension exercise guidelines"
        })
    
    # Pregnancy considerations
    if patient_profile.get("pregnant", False):
        trimester = patient_profile.get("trimester", 1)
        
        if exercise_data.get("position", "").lower() == "supine" and trimester > 1:
            relative_contraindications.append({
                "category": "Pregnancy",
                "contraindication": "Supine exercises after first trimester",
                "severity": "RELATIVE",
                "recommendation": "Modify to side-lying or inclined positions",
                "evidence": "ACOG exercise guidelines"
            })
        
        if exercise_data.get("type", "").lower() in ["contact", "high_impact"]:
            relative_contraindications.append({
                "category": "Pregnancy",
                "contraindication": "Contact or high-impact exercise during pregnancy",
                "severity": "RELATIVE",
                "recommendation": "Substitute with low-impact alternatives",
                "evidence": "Prenatal exercise research"
            })
    
    # Medication interactions
    medications = patient_profile.get("medications", [])
    
    if "beta_blockers" in medications:
        relative_contraindications.append({
            "category": "Medication",
            "contraindication": "Beta-blocker use affecting heart rate response",
            "severity": "RELATIVE",
            "recommendation": "Use RPE instead of heart rate for intensity",
            "evidence": "Exercise pharmacology"
        })
    
    if "blood_thinners" in medications and exercise_data.get("contact_risk", False):
        relative_contraindications.append({
            "category": "Medication",
            "contraindication": "Anticoagulant use with contact exercise",
            "severity": "RELATIVE",
            "recommendation": "Avoid exercises with fall/contact risk",
            "evidence": "Anticoagulation guidelines"
        })
    
    # Injury-specific relative contraindications
    injury_type = injury_data.get("injury_type", "")
    injury_phase = injury_data.get("phase", "early")
    
    if injury_type == "concussion" and exercise_data.get("cognitive_demand", "low") == "high":
        relative_contraindications.append({
            "category": "Injury-Specific",
            "contraindication": "High cognitive demand exercise post-concussion",
            "severity": "RELATIVE",
            "recommendation": "Simplify movement patterns initially",
            "evidence": "Concussion exercise guidelines"
        })
    
    return relative_contraindications

def check_exercise_precautions(exercise_data, injury_data, patient_profile):
    """Check for exercise-specific precautions"""
    
    precautions = []
    
    injury_type = injury_data.get("injury_type", "")
    injury_phase = injury_data.get("phase", "early")
    exercise_type = exercise_data.get("type", "")
    
    # Injury-specific exercise precautions
    injury_exercise_matrix = {
        "ACL": {
            "early": {
                "avoid": ["pivot", "cutting", "jumping"],
                "caution": ["closed_chain", "deep_squat"],
                "safe": ["isometric", "passive_rom", "straight_plane"]
            },
            "mid": {
                "avoid": ["unrestricted_pivot", "competitive_drills"],
                "caution": ["plyometric", "sport_specific"],
                "safe": ["progressive_strengthening", "controlled_movement"]
            },
            "late": {
                "avoid": ["unpredictable_movements"],
                "caution": ["reactive_drills", "full_speed"],
                "safe": ["planned_agility", "progressive_sport_drills"]
            }
        },
        "Achilles": {
            "early": {
                "avoid": ["jumping", "running", "calf_raises"],
                "caution": ["weight_bearing", "dorsiflexion_stretch"],
                "safe": ["non_weight_bearing", "passive_movement"]
            },
            "mid": {
                "avoid": ["high_impact", "explosive_movement"],
                "caution": ["eccentric_loading", "plyometric"],
                "safe": ["progressive_loading", "controlled_strengthening"]
            }
        },
        "Hamstring": {
            "early": {
                "avoid": ["sprinting", "aggressive_stretching", "eccentric_loading"],
                "caution": ["hip_flexion", "knee_extension"],
                "safe": ["isometric", "gentle_movement", "pain_free_rom"]
            },
            "mid": {
                "avoid": ["ballistic_movements", "max_effort"],
                "caution": ["eccentric_strengthening", "running"],
                "safe": ["progressive_strengthening", "controlled_movement"]
            }
        },
        "Rotator_Cuff": {
            "early": {
                "avoid": ["overhead", "behind_back", "heavy_lifting"],
                "caution": ["external_rotation", "abduction"],
                "safe": ["pendulum", "passive_rom", "gentle_strengthening"]
            },
            "mid": {
                "avoid": ["overhead_sports", "heavy_resistance"],
                "caution": ["progressive_overhead", "resistance_training"],
                "safe": ["strengthening", "functional_movement"]
            }
        }
    }
    
    # Check injury-specific precautions
    if injury_type in injury_exercise_matrix:
        phase_precautions = injury_exercise_matrix[injury_type].get(injury_phase, {})
        
        # Check if exercise is in avoid list
        for avoided_exercise in phase_precautions.get("avoid", []):
            if avoided_exercise.lower() in exercise_type.lower() or avoided_exercise.lower() in exercise_data.get("name", "").lower():
                precautions.append({
                    "category": "Injury-Specific",
                    "precaution": f"Exercise type contraindicated for {injury_type} in {injury_phase} phase",
                    "severity": "HIGH",
                    "recommendation": f"Avoid {avoided_exercise} exercises",
                    "alternative": suggest_alternative_exercise(avoided_exercise, injury_type, injury_phase)
                })
        
        # Check if exercise needs caution
        for caution_exercise in phase_precautions.get("caution", []):
            if caution_exercise.lower() in exercise_type.lower() or caution_exercise.lower() in exercise_data.get("name", "").lower():
                precautions.append({
                    "category": "Injury-Specific",
                    "precaution": f"Exercise requires caution for {injury_type} in {injury_phase} phase",
                    "severity": "MEDIUM",
                    "recommendation": f"Proceed carefully with {caution_exercise} exercises",
                    "modifications": suggest_exercise_modifications(caution_exercise, injury_type, injury_phase)
                })
    
    # Pain-based precautions
    pain_level = injury_data.get("current_pain", 0)
    if pain_level > 3 and exercise_data.get("load_bearing", True):
        precautions.append({
            "category": "Pain-Based",
            "precaution": "Moderate pain with load-bearing exercise",
            "severity": "MEDIUM",
            "recommendation": "Reduce load or switch to non-weight bearing alternative"
        })
    
    # Range of motion precautions
    rom_limitation = injury_data.get("rom_limitation", 0)  # Percentage of normal
    if rom_limitation > 20 and exercise_data.get("rom_requirement", "full") == "full":
        precautions.append({
            "category": "Range of Motion",
            "precaution": "Exercise requires ROM beyond current capability",
            "severity": "MEDIUM",
            "recommendation": "Modify exercise to work within available range"
        })
    
    return precautions

def suggest_alternative_exercise(avoided_exercise, injury_type, injury_phase):
    """Suggest safe alternative exercises"""
    
    alternatives = {
        "jumping": {
            "ACL": {"early": "Stationary bike", "mid": "Step-ups", "late": "Controlled hops"},
            "Achilles": {"early": "Upper body cardio", "mid": "Pool walking", "late": "Low-impact plyometrics"}
        },
        "running": {
            "Achilles": {"early": "Cycling", "mid": "Elliptical", "late": "Treadmill walking"},
            "Hamstring": {"early": "Swimming", "mid": "Walking", "late": "Jogging"}
        },
        "overhead": {
            "Rotator_Cuff": {"early": "Below shoulder exercises", "mid": "Limited overhead", "late": "Progressive overhead"}
        }
    }
    
    return alternatives.get(avoided_exercise, {}).get(injury_type, {}).get(injury_phase, "Consult with therapist for alternatives")

def suggest_exercise_modifications(exercise_type, injury_type, injury_phase):
    """Suggest modifications to make exercises safer"""
    
    modifications = {
        "plyometric": [
            "Reduce jump height",
            "Add pause between reps",
            "Use bilateral instead of unilateral",
            "Land on softer surface"
        ],
        "strengthening": [
            "Reduce load by 50%",
            "Increase rest periods",
            "Focus on concentric phase",
            "Use partial range of motion"
        ],
        "stretching": [
            "Reduce stretch intensity",
            "Hold for shorter duration",
            "Use active vs passive stretching",
            "Warm up thoroughly first"
        ]
    }
    
    return modifications.get(exercise_type, ["Reduce intensity", "Monitor symptoms", "Progress gradually"])

def generate_exercise_modifications(contraindications, exercise_data, injury_data):
    """Generate specific exercise modifications based on contraindications"""
    
    modifications = []
    
    # Intensity modifications
    if any(c.get("severity") == "RELATIVE" for c in contraindications["relative"]):
        modifications.append({
            "type": "Intensity",
            "modification": "Reduce exercise intensity by 25-50%",
            "rationale": "Relative contraindications present"
        })
    
    # Duration modifications
    if contraindications["precautions"]:
        modifications.append({
            "type": "Duration", 
            "modification": "Reduce exercise duration, increase rest periods",
            "rationale": "Precautions require careful monitoring"
        })
    
    # Position modifications
    if any("supine" in str(c) for c in contraindications["relative"]):
        modifications.append({
            "type": "Position",
            "modification": "Avoid supine positions, use inclined or side-lying",
            "rationale": "Position-specific contraindication"
        })
    
    # Load modifications
    injury_phase = injury_data.get("phase", "early")
    if injury_phase == "early":
        modifications.append({
            "type": "Load",
            "modification": "Use bodyweight or minimal resistance only",
            "rationale": "Early phase injury protection"
        })
    
    return modifications

def determine_safety_level(contraindications):
    """Determine overall safety level for exercise prescription"""
    
    absolute_count = len(contraindications["absolute"])
    relative_count = len(contraindications["relative"])
    precaution_count = len(contraindications["precautions"])
    
    if absolute_count > 0:
        safety_level = "UNSAFE"
        color = "red"
        recommendation = "Exercise prohibited - address contraindications first"
    elif relative_count >= 3 or precaution_count >= 4:
        safety_level = "HIGH_RISK"
        color = "orange"
        recommendation = "Significant modifications required - consider alternative exercises"
    elif relative_count >= 1 or precaution_count >= 2:
        safety_level = "MODERATE_RISK"
        color = "yellow"
        recommendation = "Exercise with modifications and close monitoring"
    elif precaution_count >= 1:
        safety_level = "LOW_RISK"
        color = "light_green"
        recommendation = "Exercise with minor modifications"
    else:
        safety_level = "SAFE"
        color = "green"
        recommendation = "Exercise cleared as prescribed"
    
    return {
        "level": safety_level,
        "color": color,
        "recommendation": recommendation,
        "risk_factors": {
            "absolute": absolute_count,
            "relative": relative_count,
            "precautions": precaution_count
        }
    }

def create_safety_checklist(injury_type, exercise_type):
    """Create a pre-exercise safety checklist"""
    
    general_checklist = [
        "Patient has been medically cleared for exercise",
        "Vital signs are within normal limits",
        "No fever or signs of infection",
        "Patient understands exercise instructions",
        "Emergency procedures are in place"
    ]
    
    injury_specific_checklists = {
        "ACL": [
            "Knee swelling is minimal",
            "No episodes of giving way in past week",
            "Can perform exercise without knee brace (if applicable)",
            "No sharp pain with movement"
        ],
        "Concussion": [
            "No headache for 24 hours",
            "Normal cognitive function",
            "No dizziness or balance issues",
            "Cleared by physician for physical activity"
        ],
        "Cardiac": [
            "Resting heart rate and blood pressure normal",
            "No chest pain or shortness of breath",
            "Medications taken as prescribed",
            "Emergency contact information available"
        ]
    }
    
    checklist = general_checklist.copy()
    if injury_type in injury_specific_checklists:
        checklist.extend(injury_specific_checklists[injury_type])
    
    return {
        "checklist_items": checklist,
        "injury_type": injury_type,
        "exercise_type": exercise_type,
        "date_created": datetime.now().strftime("%Y-%m-%d")
    }

def monitor_exercise_response(exercise_data, patient_response):
    """Monitor patient response during exercise for safety"""
    
    warning_signs = []
    
    # Vital sign monitoring
    heart_rate = patient_response.get("heart_rate", 0)
    max_predicted_hr = 220 - patient_response.get("age", 30)
    
    if heart_rate > max_predicted_hr * 0.85:
        warning_signs.append({
            "sign": "Elevated heart rate",
            "value": heart_rate,
            "threshold": max_predicted_hr * 0.85,
            "action": "Reduce exercise intensity"
        })
    
    # Symptom monitoring
    pain_level = patient_response.get("pain_level", 0)
    if pain_level > 3:
        warning_signs.append({
            "sign": "Elevated pain",
            "value": pain_level,
            "threshold": 3,
            "action": "Stop exercise, assess injury status"
        })
    
    # Exertion monitoring
    rpe = patient_response.get("rpe", 6)
    if rpe > 17:  # Very hard exertion
        warning_signs.append({
            "sign": "High perceived exertion",
            "value": rpe,
            "threshold": 17,
            "action": "Reduce exercise intensity or duration"
        })
    
    return {
        "warning_signs": warning_signs,
        "continue_exercise": len(warning_signs) == 0,
        "monitoring_recommendations": generate_monitoring_recommendations(warning_signs)
    }

def generate_monitoring_recommendations(warning_signs):
    """Generate recommendations based on exercise response monitoring"""
    
    if not warning_signs:
        return ["Continue exercise as prescribed", "Monitor for any changes in symptoms"]
    
    recommendations = []
    
    for sign in warning_signs:
        if "heart rate" in sign["sign"]:
            recommendations.append("Implement heart rate monitoring throughout session")
        elif "pain" in sign["sign"]:
            recommendations.append("Stop exercise immediately and reassess")
        elif "exertion" in sign["sign"]:
            recommendations.append("Reduce intensity and allow for longer rest periods")
    
    recommendations.append("Document all warning signs and patient responses")
    recommendations.append("Consider modifying future exercise prescriptions")
    
    return recommendations