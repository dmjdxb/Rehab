"""
Treatment Plan Templates
Evidence-based, standardized treatment protocols for common injuries
"""

from datetime import datetime, timedelta
import json

def generate_treatment_plan(injury_data, patient_profile, treatment_goals):
    """
    Generate comprehensive, evidence-based treatment plan
    
    Based on: Clinical practice guidelines and systematic reviews
    """
    
    injury_type = injury_data.get("injury_type", "ACL")
    injury_severity = injury_data.get("severity", "moderate")
    treatment_approach = injury_data.get("treatment_approach", "conservative")
    
    # Get appropriate template
    template = get_treatment_template(injury_type, injury_severity, treatment_approach)
    
    # Customize template based on patient factors
    customized_plan = customize_treatment_plan(template, patient_profile, treatment_goals)
    
    # Generate timeline and milestones
    timeline = generate_treatment_timeline(customized_plan, injury_data)
    
    # Create documentation
    documentation = generate_plan_documentation(customized_plan, timeline, patient_profile)
    
    return {
        "treatment_plan": customized_plan,
        "timeline": timeline,
        "documentation": documentation,
        "plan_id": f"{injury_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

def get_treatment_template(injury_type, severity, approach):
    """Get evidence-based treatment template for specific injury"""
    
    templates = {
        "ACL": {
            "conservative": {
                "overview": "Evidence-based ACL conservative management protocol",
                "duration_weeks": 16,
                "phases": {
                    "acute": {
                        "duration": "0-2 weeks",
                        "goals": [
                            "Control pain and swelling",
                            "Restore full knee extension",
                            "Initiate quadriceps activation",
                            "Restore normal gait pattern"
                        ],
                        "interventions": [
                            "RICE protocol",
                            "Pain management",
                            "Gentle range of motion",
                            "Quadriceps setting exercises",
                            "Straight leg raises",
                            "Heel slides",
                            "Stationary bike (pain-free ROM)"
                        ],
                        "criteria_to_progress": [
                            "Full knee extension",
                            "Minimal pain and swelling",
                            "Good quadriceps control",
                            "Normal gait without aids"
                        ]
                    },
                    "early": {
                        "duration": "2-6 weeks",
                        "goals": [
                            "Achieve full ROM",
                            "Normalize gait",
                            "Begin strengthening",
                            "Improve proprioception"
                        ],
                        "interventions": [
                            "Progressive strengthening",
                            "Closed-chain exercises",
                            "Balance training",
                            "Pool therapy",
                            "Manual therapy",
                            "Functional movement training"
                        ],
                        "criteria_to_progress": [
                            "Full pain-free ROM",
                            "4/5 quadriceps strength",
                            "Normal single-leg stance >30 sec",
                            "Pain <3/10 with activities"
                        ]
                    },
                    "intermediate": {
                        "duration": "6-12 weeks",
                        "goals": [
                            "Restore strength to >85% of uninvolved side",
                            "Begin sport-specific training",
                            "Improve neuromuscular control",
                            "Return to straight-line running"
                        ],
                        "interventions": [
                            "Progressive resistance training",
                            "Plyometric exercises",
                            "Agility drills",
                            "Sport-specific movements",
                            "Running progression",
                            "Advanced balance training"
                        ],
                        "criteria_to_progress": [
                            "LSI >85% for strength",
                            "Hop test LSI >85%",
                            "No pain with running",
                            "Normal movement patterns"
                        ]
                    },
                    "advanced": {
                        "duration": "12-16 weeks",
                        "goals": [
                            "Return to sport activities",
                            "LSI >90% all tests",
                            "Confident in knee stability",
                            "Sport-specific clearance"
                        ],
                        "interventions": [
                            "High-level plyometrics",
                            "Cutting and pivoting drills",
                            "Sport-specific training",
                            "Return-to-sport testing",
                            "Psychological readiness assessment"
                        ],
                        "criteria_to_progress": [
                            "LSI >90% all hop tests",
                            "Strength LSI >90%",
                            "Psychological readiness",
                            "Sport-specific clearance"
                        ]
                    }
                }
            },
            "surgical": {
                "overview": "Post-operative ACL reconstruction protocol",
                "duration_weeks": 24,
                "phases": {
                    "immediate_post_op": {
                        "duration": "0-2 weeks",
                        "goals": [
                            "Protect surgical site",
                            "Control pain and swelling",
                            "Restore knee extension",
                            "Begin quadriceps activation"
                        ],
                        "interventions": [
                            "Immobilization per surgeon",
                            "Cryotherapy",
                            "Elevation",
                            "Pain management",
                            "Ankle pumps",
                            "Quadriceps sets",
                            "Passive ROM as tolerated"
                        ],
                        "precautions": [
                            "Weight bearing per surgeon",
                            "ROM limits per protocol",
                            "No active hamstring exercises",
                            "Brace compliance"
                        ]
                    },
                    "early_rehab": {
                        "duration": "2-6 weeks",
                        "goals": [
                            "Full knee extension",
                            "Flexion to 90° by week 4",
                            "Independent ambulation",
                            "Quadriceps strength 4/5"
                        ],
                        "interventions": [
                            "Progressive ROM exercises",
                            "Closed-chain strengthening",
                            "Stationary bike",
                            "Pool walking",
                            "Balance training",
                            "Scar mobilization"
                        ]
                    }
                    # Additional phases would continue...
                }
            }
        },
        "Hamstring": {
            "acute": {
                "overview": "Acute hamstring strain management",
                "duration_weeks": 8,
                "phases": {
                    "acute": {
                        "duration": "0-5 days",
                        "goals": [
                            "Control pain and bleeding",
                            "Protect healing tissue",
                            "Maintain pain-free ROM",
                            "Begin early mobilization"
                        ],
                        "interventions": [
                            "PEACE protocol (24-48hrs)",
                            "Gentle pain-free movement",
                            "Isometric strengthening",
                            "Soft tissue massage",
                            "Heat before activity"
                        ],
                        "avoid": [
                            "Aggressive stretching",
                            "Painful movements",
                            "Anti-inflammatory drugs (first 48hrs)",
                            "Deep tissue massage"
                        ]
                    },
                    "subacute": {
                        "duration": "5 days - 3 weeks",
                        "goals": [
                            "Restore pain-free ROM",
                            "Begin strengthening",
                            "Improve tissue quality",
                            "Progress functional activities"
                        ],
                        "interventions": [
                            "Progressive stretching",
                            "Eccentric strengthening",
                            "Manual therapy",
                            "Progressive loading",
                            "Running preparation"
                        ]
                    }
                }
            }
        },
        "Rotator_Cuff": {
            "conservative": {
                "overview": "Conservative rotator cuff management",
                "duration_weeks": 12,
                "phases": {
                    "pain_control": {
                        "duration": "0-2 weeks",
                        "goals": [
                            "Reduce pain and inflammation",
                            "Restore pain-free ROM",
                            "Patient education",
                            "Activity modification"
                        ],
                        "interventions": [
                            "Activity modification",
                            "Pain management",
                            "Gentle ROM exercises",
                            "Pendulum exercises",
                            "Postural correction"
                        ]
                    },
                    "mobility_restoration": {
                        "duration": "2-6 weeks",
                        "goals": [
                            "Restore full ROM",
                            "Begin strengthening",
                            "Improve scapular function",
                            "Address impairments"
                        ],
                        "interventions": [
                            "Progressive ROM exercises",
                            "Scapular stabilization",
                            "Rotator cuff strengthening",
                            "Manual therapy",
                            "Therapeutic exercise"
                        ]
                    }
                }
            }
        }
    }
    
    # Get specific template or default
    injury_templates = templates.get(injury_type, templates["ACL"])
    return injury_templates.get(approach, injury_templates.get("conservative", injury_templates[list(injury_templates.keys())[0]]))

def customize_treatment_plan(template, patient_profile, treatment_goals):
    """Customize template based on individual patient factors"""
    
    customized_plan = template.copy()
    
    # Adjust based on patient age
    age = patient_profile.get("age", 30)
    if age > 65:
        # Slower progression for older adults
        for phase in customized_plan["phases"].values():
            if "duration" in phase:
                # Extend phase duration by 25%
                phase["duration_modifier"] = 1.25
                phase["notes"] = phase.get("notes", []) + ["Extended timeline for older adult"]
    
    elif age < 18:
        # Consider growth factors for adolescents
        for phase in customized_plan["phases"].values():
            phase["notes"] = phase.get("notes", []) + ["Monitor for growth-related factors"]
    
    # Adjust based on activity level
    activity_level = patient_profile.get("activity_level", "recreational")
    if activity_level == "elite":
        # More aggressive progression
        customized_plan["duration_weeks"] = int(customized_plan["duration_weeks"] * 0.9)
        customized_plan["notes"] = ["Accelerated protocol for elite athlete"]
    
    # Adjust based on comorbidities
    comorbidities = patient_profile.get("comorbidities", [])
    if "diabetes" in comorbidities:
        for phase in customized_plan["phases"].values():
            phase["notes"] = phase.get("notes", []) + ["Monitor wound healing - diabetes present"]
    
    if "osteoporosis" in comorbidities:
        for phase in customized_plan["phases"].values():
            phase["precautions"] = phase.get("precautions", []) + ["Avoid high-impact activities"]
    
    # Adjust based on treatment goals
    primary_goal = treatment_goals.get("primary_goal", "return_to_function")
    if primary_goal == "return_to_sport":
        # Add sport-specific phases
        customized_plan["sport_specific_training"] = True
        customized_plan["rts_testing_required"] = True
    
    elif primary_goal == "pain_relief":
        # Emphasize pain management strategies
        for phase in customized_plan["phases"].values():
            phase["pain_focus"] = True
    
    return customized_plan

def generate_treatment_timeline(treatment_plan, injury_data):
    """Generate detailed timeline with milestones"""
    
    start_date = datetime.strptime(injury_data.get("start_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
    
    timeline = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "total_duration_weeks": treatment_plan["duration_weeks"],
        "phases": {},
        "milestones": {},
        "reassessment_dates": []
    }
    
    current_date = start_date
    
    for phase_name, phase_data in treatment_plan["phases"].items():
        # Parse duration
        duration_str = phase_data.get("duration", "4 weeks")
        duration_weeks = parse_duration(duration_str)
        
        # Apply any duration modifiers
        duration_modifier = phase_data.get("duration_modifier", 1.0)
        adjusted_duration = duration_weeks * duration_modifier
        
        phase_end_date = current_date + timedelta(weeks=adjusted_duration)
        
        timeline["phases"][phase_name] = {
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": phase_end_date.strftime("%Y-%m-%d"),
            "duration_weeks": round(adjusted_duration, 1),
            "goals": phase_data.get("goals", []),
            "key_interventions": phase_data.get("interventions", [])[:3],  # Top 3 interventions
            "progression_criteria": phase_data.get("criteria_to_progress", [])
        }
        
        # Add reassessment date (middle of phase)
        reassessment_date = current_date + timedelta(weeks=adjusted_duration/2)
        timeline["reassessment_dates"].append({
            "date": reassessment_date.strftime("%Y-%m-%d"),
            "phase": phase_name,
            "focus": "Progress evaluation and plan adjustment"
        })
        
        current_date = phase_end_date
    
    # Add key milestones
    timeline["milestones"] = generate_treatment_milestones(timeline, injury_data)
    
    return timeline

def parse_duration(duration_str):
    """Parse duration string to weeks"""
    
    if "week" in duration_str.lower():
        # Extract number before "week"
        import re
        numbers = re.findall(r'\d+', duration_str)
        if len(numbers) == 1:
            return int(numbers[0])
        elif len(numbers) == 2:
            # Range like "2-6 weeks", take average
            return (int(numbers[0]) + int(numbers[1])) / 2
    
    elif "day" in duration_str.lower():
        numbers = re.findall(r'\d+', duration_str)
        if numbers:
            return int(numbers[0]) / 7  # Convert days to weeks
    
    return 4  # Default to 4 weeks

def generate_treatment_milestones(timeline, injury_data):
    """Generate key treatment milestones"""
    
    injury_type = injury_data.get("injury_type", "ACL")
    
    # Common milestones for all injuries
    milestones = {
        "pain_free_date": {
            "target_date": calculate_milestone_date(timeline, 0.3),  # 30% through treatment
            "description": "Expected pain-free activities of daily living",
            "assessment": "Pain rating <2/10 with normal activities"
        },
        "full_rom_date": {
            "target_date": calculate_milestone_date(timeline, 0.4),  # 40% through treatment
            "description": "Full range of motion restored",
            "assessment": "ROM within 5° of unaffected side"
        },
        "strength_milestone": {
            "target_date": calculate_milestone_date(timeline, 0.7),  # 70% through treatment
            "description": "Strength >80% of unaffected side",
            "assessment": "Manual muscle testing or instrumented testing"
        }
    }
    
    # Injury-specific milestones
    if injury_type == "ACL":
        milestones.update({
            "running_clearance": {
                "target_date": calculate_milestone_date(timeline, 0.6),
                "description": "Clearance for straight-line running",
                "assessment": "Hop test LSI >80%, no pain with jogging"
            },
            "rts_testing": {
                "target_date": calculate_milestone_date(timeline, 0.9),
                "description": "Return-to-sport testing battery",
                "assessment": "Comprehensive hop tests, strength testing, psychological readiness"
            }
        })
    
    elif injury_type == "Rotator_Cuff":
        milestones.update({
            "overhead_activities": {
                "target_date": calculate_milestone_date(timeline, 0.8),
                "description": "Return to overhead activities",
                "assessment": "Pain-free overhead motion, adequate strength"
            }
        })
    
    return milestones

def calculate_milestone_date(timeline, percentage):
    """Calculate milestone date as percentage of total treatment"""
    
    start_date = datetime.strptime(timeline["start_date"], "%Y-%m-%d")
    total_weeks = timeline["total_duration_weeks"]
    milestone_weeks = total_weeks * percentage
    
    milestone_date = start_date + timedelta(weeks=milestone_weeks)
    return milestone_date.strftime("%Y-%m-%d")

def generate_plan_documentation(treatment_plan, timeline, patient_profile):
    """Generate comprehensive treatment plan documentation"""
    
    documentation = {
        "patient_information": {
            "name": patient_profile.get("name", "Patient"),
            "age": patient_profile.get("age", ""),
            "diagnosis": patient_profile.get("diagnosis", ""),
            "date_of_injury": patient_profile.get("injury_date", ""),
            "physician": patient_profile.get("physician", ""),
            "therapist": patient_profile.get("therapist", "")
        },
        "treatment_summary": {
            "protocol_name": treatment_plan.get("overview", ""),
            "total_duration": f"{treatment_plan['duration_weeks']} weeks",
            "number_of_phases": len(treatment_plan["phases"]),
            "primary_goals": extract_primary_goals(treatment_plan),
            "key_interventions": extract_key_interventions(treatment_plan)
        },
        "phase_breakdown": generate_phase_documentation(treatment_plan, timeline),
        "outcome_measures": recommend_outcome_measures(patient_profile),
        "precautions_and_contraindications": extract_precautions(treatment_plan),
        "home_exercise_program": generate_hep_guidelines(treatment_plan),
        "follow_up_schedule": generate_followup_schedule(timeline)
    }
    
    return documentation

def extract_primary_goals(treatment_plan):
    """Extract primary goals across all phases"""
    
    all_goals = []
    for phase in treatment_plan["phases"].values():
        all_goals.extend(phase.get("goals", []))
    
    # Remove duplicates and prioritize
    unique_goals = list(dict.fromkeys(all_goals))
    return unique_goals[:5]  # Top 5 goals

def extract_key_interventions(treatment_plan):
    """Extract key interventions across all phases"""
    
    all_interventions = []
    for phase in treatment_plan["phases"].values():
        all_interventions.extend(phase.get("interventions", []))
    
    # Count frequency and return most common
    from collections import Counter
    intervention_counts = Counter(all_interventions)
    return [intervention for intervention, count in intervention_counts.most_common(5)]

def generate_phase_documentation(treatment_plan, timeline):
    """Generate detailed phase documentation"""
    
    phase_docs = {}
    
    for phase_name, phase_data in treatment_plan["phases"].items():
        timeline_data = timeline["phases"].get(phase_name, {})
        
        phase_docs[phase_name] = {
            "duration": timeline_data.get("duration_weeks", 0),
            "dates": f"{timeline_data.get('start_date', '')} to {timeline_data.get('end_date', '')}",
            "primary_goals": phase_data.get("goals", [])[:3],
            "key_interventions": phase_data.get("interventions", [])[:5],
            "progression_criteria": phase_data.get("criteria_to_progress", []),
            "precautions": phase_data.get("precautions", []),
            "frequency": phase_data.get("frequency", "3x/week"),
            "estimated_sessions": calculate_estimated_sessions(timeline_data.get("duration_weeks", 0))
        }
    
    return phase_docs

def calculate_estimated_sessions(duration_weeks):
    """Calculate estimated number of therapy sessions"""
    
    if duration_weeks <= 2:
        sessions_per_week = 3
    elif duration_weeks <= 6:
        sessions_per_week = 2.5
    else:
        sessions_per_week = 2
    
    return round(duration_weeks * sessions_per_week)

def recommend_outcome_measures(patient_profile):
    """Recommend appropriate outcome measures"""
    
    injury_type = patient_profile.get("injury_type", "")
    
    outcome_measures = {
        "all_injuries": [
            "Numeric Pain Rating Scale (NPRS)",
            "Global Rating of Change (GROC)",
            "Patient Specific Functional Scale (PSFS)"
        ],
        "ACL": [
            "International Knee Documentation Committee (IKDC)",
            "Knee Injury and Osteoarthritis Outcome Score (KOOS)",
            "Lysholm Knee Score"
        ],
        "Rotator_Cuff": [
            "Disabilities of Arm, Shoulder, and Hand (DASH)",
            "American Shoulder and Elbow Surgeons Score (ASES)",
            "Western Ontario Rotator Cuff Index (WORC)"
        ],
        "Hamstring": [
            "Lower Extremity Functional Scale (LEFS)",
            "Hamstring Outcome Score (HOS)"
        ]
    }
    
    recommended = outcome_measures["all_injuries"].copy()
    if injury_type in outcome_measures:
        recommended.extend(outcome_measures[injury_type])
    
    return {
        "baseline_assessment": recommended,
        "reassessment_frequency": "Every 2-4 weeks",
        "discharge_assessment": recommended + ["Patient satisfaction survey"]
    }

def extract_precautions(treatment_plan):
    """Extract all precautions from treatment plan"""
    
    all_precautions = []
    for phase in treatment_plan["phases"].values():
        all_precautions.extend(phase.get("precautions", []))
        all_precautions.extend(phase.get("avoid", []))
    
    return list(set(all_precautions))  # Remove duplicates

def generate_hep_guidelines(treatment_plan):
    """Generate home exercise program guidelines"""
    
    return {
        "frequency": "Daily for mobility, 3x/week for strengthening",
        "duration": "20-30 minutes per session",
        "progression": "Increase difficulty every 1-2 weeks based on symptoms",
        "monitoring": "Track pain levels and function improvements",
        "red_flags": [
            "Increased pain >24 hours after exercise",
            "New swelling or inflammation", 
            "Loss of motion or function",
            "Any concerning symptoms"
        ],
        "contact_instructions": "Contact therapist if red flags occur or questions arise"
    }

def generate_followup_schedule(timeline):
    """Generate follow-up and reassessment schedule"""
    
    followup_schedule = []
    
    # Add reassessment dates
    for reassessment in timeline.get("reassessment_dates", []):
        followup_schedule.append({
            "date": reassessment["date"],
            "type": "Progress Assessment",
            "focus": reassessment["focus"],
            "duration": "60 minutes"
        })
    
    # Add milestone check dates
    for milestone_name, milestone_data in timeline.get("milestones", {}).items():
        followup_schedule.append({
            "date": milestone_data["target_date"],
            "type": "Milestone Assessment",
            "focus": milestone_data["description"],
            "assessment": milestone_data["assessment"]
        })
    
    # Sort by date
    followup_schedule.sort(key=lambda x: x["date"])
    
    return followup_schedule

def export_treatment_plan(treatment_plan_data, format_type="pdf"):
    """Export treatment plan to various formats"""
    
    export_data = {
        "plan_summary": treatment_plan_data["treatment_plan"]["overview"],
        "timeline": treatment_plan_data["timeline"],
        "documentation": treatment_plan_data["documentation"],
        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "format": format_type
    }
    
    # This would integrate with actual export libraries
    return {
        "export_successful": True,
        "export_data": export_data,
        "file_name": f"treatment_plan_{treatment_plan_data['plan_id']}.{format_type}"
    }