"""
Rehabilitation Phase Determination Engine
Evidence-based logic for determining rehab progression phases
"""

def get_rehab_phase(injury_type, peak_force, lsi, rfd, pain_score):
    """
    Determine rehabilitation phase based on clinical metrics
    
    Args:
        injury_type (str): Type of injury
        peak_force (float): Peak force measurement in Newtons
        lsi (float): Limb Symmetry Index percentage (0-100)
        rfd (float): Rate of Force Development as percentage of baseline
        pain_score (int): Pain score 0-10
    
    Returns:
        dict: Contains 'phase' and 'message' with recommendations
    """
    
    # Define injury-specific thresholds
    injury_thresholds = {
        "ACL": {
            "early_to_mid": {"lsi": 70, "rfd": 60, "pain": 4},
            "mid_to_late": {"lsi": 85, "rfd": 80, "pain": 2},
            "late_to_rts": {"lsi": 90, "rfd": 90, "pain": 1}
        },
        "Achilles": {
            "early_to_mid": {"lsi": 65, "rfd": 50, "pain": 5},
            "mid_to_late": {"lsi": 80, "rfd": 75, "pain": 3},
            "late_to_rts": {"lsi": 90, "rfd": 85, "pain": 1}
        },
        "Hamstring": {
            "early_to_mid": {"lsi": 75, "rfd": 65, "pain": 4},
            "mid_to_late": {"lsi": 85, "rfd": 80, "pain": 2},
            "late_to_rts": {"lsi": 90, "rfd": 90, "pain": 1}
        },
        "Patellar Tendon": {
            "early_to_mid": {"lsi": 70, "rfd": 55, "pain": 4},
            "mid_to_late": {"lsi": 85, "rfd": 75, "pain": 2},
            "late_to_rts": {"lsi": 90, "rfd": 85, "pain": 1}
        },
        "Rotator Cuff": {
            "early_to_mid": {"lsi": 65, "rfd": 50, "pain": 5},
            "mid_to_late": {"lsi": 80, "rfd": 70, "pain": 3},
            "late_to_rts": {"lsi": 85, "rfd": 80, "pain": 1}
        },
        "Groin": {
            "early_to_mid": {"lsi": 70, "rfd": 60, "pain": 4},
            "mid_to_late": {"lsi": 85, "rfd": 80, "pain": 2},
            "late_to_rts": {"lsi": 90, "rfd": 85, "pain": 1}
        },
        "Proximal Hamstring Tendinopathy": {
            "early_to_mid": {"lsi": 70, "rfd": 60, "pain": 5},
            "mid_to_late": {"lsi": 80, "rfd": 75, "pain": 3},
            "late_to_rts": {"lsi": 90, "rfd": 85, "pain": 1}
        },
        "ATFL Ligament Injury": {
            "early_to_mid": {"lsi": 75, "rfd": 65, "pain": 4},
            "mid_to_late": {"lsi": 85, "rfd": 80, "pain": 2},
            "late_to_rts": {"lsi": 90, "rfd": 90, "pain": 1}
        }
    }
    
    # Get thresholds for specific injury or use default ACL values
    thresholds = injury_thresholds.get(injury_type, injury_thresholds["ACL"])
    
    # Phase determination logic
    if pain_score > thresholds["early_to_mid"]["pain"]:
        phase = "Early"
        message = f"High pain score ({pain_score}/10) indicates early phase. Focus on pain management and gentle mobility."
        
    elif (lsi < thresholds["early_to_mid"]["lsi"] or 
          rfd < thresholds["early_to_mid"]["rfd"]):
        phase = "Early"
        message = f"LSI ({lsi}%) or RFD ({rfd}%) below early phase thresholds. Continue foundational strengthening."
        
    elif (pain_score > thresholds["mid_to_late"]["pain"] or
          lsi < thresholds["mid_to_late"]["lsi"] or 
          rfd < thresholds["mid_to_late"]["rfd"]):
        phase = "Mid"
        message = f"Progressing well. LSI: {lsi}%, RFD: {rfd}%. Continue progressive loading."
        
    elif (pain_score > thresholds["late_to_rts"]["pain"] or
          lsi < thresholds["late_to_rts"]["lsi"] or 
          rfd < thresholds["late_to_rts"]["rfd"]):
        phase = "Late"
        message = f"Advanced phase. LSI: {lsi}%, RFD: {rfd}%. Introduce sport-specific movements."
        
    else:
        phase = "Return to Sport"
        message = f"Excellent metrics! LSI: {lsi}%, RFD: {rfd}%. Ready for sport-specific training and return to play assessment."
    
    # Additional warnings
    warnings = []
    if lsi < 90 and phase in ["Late", "Return to Sport"]:
        warnings.append("⚠️ LSI < 90% increases re-injury risk")
    if pain_score > 2 and phase in ["Late", "Return to Sport"]:
        warnings.append("⚠️ Persistent pain needs clinical review")
    if rfd < 85 and phase == "Return to Sport":
        warnings.append("⚠️ Consider more explosive strength training")
    
    if warnings:
        message += "\n\n" + "\n".join(warnings)
    
    return {
        "phase": phase,
        "message": message,
        "metrics": {
            "lsi": lsi,
            "rfd": rfd,
            "pain": pain_score,
            "peak_force": peak_force
        }
    }


def get_exercise_recommendations(injury_type, phase):
    """
    Get exercise recommendations based on injury and phase
    Now pulls actual exercises from the database
    
    Args:
        injury_type (str): Type of injury
        phase (str): Current rehabilitation phase
    
    Returns:
        dict: Contains recommendations and actual exercises from database
    """
    import pandas as pd
    import os
    
    # General recommendations by phase
    general_recommendations = {
        "Early": {
            "focus": ["Pain management", "Range of motion", "Basic strengthening"],
            "exercise_types": ["Mobility", "Isometric", "Light Strength"],
            "avoid": ["Plyometric", "High-intensity movements"]
        },
        "Mid": {
            "focus": ["Progressive strengthening", "Functional movement", "Endurance"],
            "exercise_types": ["Strength", "Mobility", "Neuromuscular"],
            "avoid": ["High-impact plyometrics"]
        },
        "Late": {
            "focus": ["Sport-specific strength", "Power development", "Movement quality"],
            "exercise_types": ["Strength", "Plyometric", "Neuromuscular"],
            "avoid": ["Excessive volume without recovery"]
        },
        "Return to Sport": {
            "focus": ["Sport-specific training", "Reactive strength", "Competition prep"],
            "exercise_types": ["Plyometric", "Neuromuscular", "Sport-specific"],
            "avoid": ["Deconditioning"]
        }
    }
    
    # Get general recommendations
    recommendations = general_recommendations.get(phase, general_recommendations["Early"])
    
    # Try to load exercise database and get specific exercises
    try:
        csv_path = "exercise_index_master.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            
            # Filter exercises for this injury and phase
            specific_exercises = df[
                (df['Injury'] == injury_type) & 
                (df['Phase'] == phase)
            ].copy()
            
            # If no specific exercises for this injury, get exercises for this phase from similar injuries
            if len(specific_exercises) == 0:
                specific_exercises = df[df['Phase'] == phase].copy()
            
            # If still no exercises, get any exercises for this injury
            if len(specific_exercises) == 0:
                specific_exercises = df[df['Injury'] == injury_type].copy()
            
            # Sort by exercise type priority for this phase
            recommended_types = recommendations["exercise_types"]
            specific_exercises['priority'] = specific_exercises['Type'].apply(
                lambda x: recommended_types.index(x) if x in recommended_types else len(recommended_types)
            )
            specific_exercises = specific_exercises.sort_values('priority').head(6)  # Top 6 exercises
            
            # Add specific exercises to recommendations
            recommendations["specific_exercises"] = specific_exercises[
                ['Exercise', 'Type', 'Goal', 'Equipment', 'Progression', 'Evidence', 'VideoURL']
            ].to_dict('records')
            
        else:
            recommendations["specific_exercises"] = []
            
    except Exception as e:
        print(f"Error loading exercise database: {e}")
        recommendations["specific_exercises"] = []
    
    return recommendations

def get_all_exercises_for_injury_phase(injury_type, phase):
    """
    Get all exercises for a specific injury and phase
    """
    import pandas as pd
    import os
    
    try:
        csv_path = "exercise_index_master.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            
            # Filter exercises
            exercises = df[
                (df['Injury'] == injury_type) & 
                (df['Phase'] == phase)
            ].copy()
            
            return exercises
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

