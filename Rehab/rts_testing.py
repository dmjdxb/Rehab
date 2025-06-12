"""
Return-to-Sport Testing Batteries
Evidence-based protocols for determining readiness to return to sport
"""

import math
from datetime import datetime
import pandas as pd

def calculate_hop_test_battery(test_results, injury_type="ACL", sport_level="recreational"):
    """
    Calculate hop test battery results with LSI and normative comparisons
    
    Based on: Reid A, et al. Br J Sports Med. 2007;41(6):369-373.
              Gokeler A, et al. Br J Sports Med. 2017;51(23):1651-1669.
    """
    
    # Hop test normative data (research-based thresholds)
    hop_thresholds = {
        "ACL": {
            "recreational": {"lsi_threshold": 90, "minimum_distance": 85},
            "competitive": {"lsi_threshold": 95, "minimum_distance": 90},
            "elite": {"lsi_threshold": 98, "minimum_distance": 95}
        },
        "Achilles": {
            "recreational": {"lsi_threshold": 85, "minimum_distance": 80},
            "competitive": {"lsi_threshold": 90, "minimum_distance": 85},
            "elite": {"lsi_threshold": 95, "minimum_distance": 90}
        },
        "Hamstring": {
            "recreational": {"lsi_threshold": 88, "minimum_distance": 82},
            "competitive": {"lsi_threshold": 92, "minimum_distance": 87},
            "elite": {"lsi_threshold": 96, "minimum_distance": 92}
        }
    }
    
    thresholds = hop_thresholds.get(injury_type, hop_thresholds["ACL"])
    level_thresholds = thresholds.get(sport_level, thresholds["recreational"])
    
    hop_tests = {
        "single_hop": {
            "name": "Single Hop for Distance",
            "injured_limb": test_results.get("single_hop_injured", 0),
            "uninjured_limb": test_results.get("single_hop_uninjured", 0),
            "weight": 0.25
        },
        "triple_hop": {
            "name": "Triple Hop for Distance", 
            "injured_limb": test_results.get("triple_hop_injured", 0),
            "uninjured_limb": test_results.get("triple_hop_uninjured", 0),
            "weight": 0.25
        },
        "crossover_hop": {
            "name": "Crossover Hop for Distance",
            "injured_limb": test_results.get("crossover_hop_injured", 0),
            "uninjured_limb": test_results.get("crossover_hop_uninjured", 0),
            "weight": 0.25
        },
        "timed_hop": {
            "name": "6m Timed Hop",
            "injured_limb": test_results.get("timed_hop_injured", 0),
            "uninjured_limb": test_results.get("timed_hop_uninjured", 0),
            "weight": 0.25,
            "reverse_scoring": True  # Lower time = better
        }
    }
    
    results = {}
    total_lsi = 0
    passed_tests = 0
    
    for test_key, test_data in hop_tests.items():
        injured = test_data["injured_limb"]
        uninjured = test_data["uninjured_limb"]
        
        if injured > 0 and uninjured > 0:
            if test_data.get("reverse_scoring", False):
                # For timed tests, lower is better
                lsi = (uninjured / injured) * 100
            else:
                # For distance tests, higher is better
                lsi = (injured / uninjured) * 100
            
            # Cap LSI at 120% (prevent unrealistic values)
            lsi = min(lsi, 120)
            
            passed = lsi >= level_thresholds["lsi_threshold"]
            
            results[test_key] = {
                "name": test_data["name"],
                "injured_result": injured,
                "uninjured_result": uninjured,
                "lsi": round(lsi, 1),
                "passed": passed,
                "threshold": level_thresholds["lsi_threshold"]
            }
            
            total_lsi += lsi * test_data["weight"]
            if passed:
                passed_tests += 1
    
    # Calculate composite scores
    composite_lsi = round(total_lsi, 1) if total_lsi > 0 else 0
    pass_rate = (passed_tests / len(results)) * 100 if results else 0
    
    # Determine overall result
    overall_passed = (
        composite_lsi >= level_thresholds["lsi_threshold"] and
        pass_rate >= 75  # Must pass at least 3/4 tests
    )
    
    # Risk assessment
    if composite_lsi >= 95:
        risk_level = "Low"
        recommendation = "Cleared for return to sport"
    elif composite_lsi >= 90:
        risk_level = "Low-Moderate"
        recommendation = "Consider sport-specific training progression"
    elif composite_lsi >= 85:
        risk_level = "Moderate"
        recommendation = "Continue strengthening, retest in 2-4 weeks"
    else:
        risk_level = "High"
        recommendation = "Significant deficits present - comprehensive rehabilitation needed"
    
    return {
        "individual_tests": results,
        "composite_lsi": composite_lsi,
        "pass_rate": round(pass_rate, 1),
        "overall_passed": overall_passed,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "injury_type": injury_type,
        "sport_level": sport_level,
        "threshold_met": level_thresholds["lsi_threshold"],
        "test_date": datetime.now().strftime("%Y-%m-%d")
    }

def calculate_strength_testing_battery(strength_data, injury_type="ACL"):
    """
    Comprehensive strength testing for RTS
    
    Based on: Schmitt LC, et al. J Orthop Sports Phys Ther. 2012;42(9):750-759.
    """
    
    strength_thresholds = {
        "ACL": {
            "knee_extension": 90,
            "knee_flexion": 90,
            "hip_abduction": 85,
            "hip_extension": 85
        },
        "Achilles": {
            "plantarflexion": 95,
            "dorsiflexion": 85,
            "inversion": 85,
            "eversion": 85
        },
        "Hamstring": {
            "knee_flexion": 95,
            "hip_extension": 90,
            "hip_abduction": 85
        }
    }
    
    thresholds = strength_thresholds.get(injury_type, strength_thresholds["ACL"])
    
    strength_results = {}
    total_strength_index = 0
    muscle_groups_tested = 0
    
    for muscle_group, threshold in thresholds.items():
        injured_key = f"{muscle_group}_injured"
        uninjured_key = f"{muscle_group}_uninjured"
        
        if injured_key in strength_data and uninjured_key in strength_data:
            injured = strength_data[injured_key]
            uninjured = strength_data[uninjured_key]
            
            if injured > 0 and uninjured > 0:
                lsi = (injured / uninjured) * 100
                passed = lsi >= threshold
                
                strength_results[muscle_group] = {
                    "injured_strength": injured,
                    "uninjured_strength": uninjured,
                    "lsi": round(lsi, 1),
                    "threshold": threshold,
                    "passed": passed
                }
                
                total_strength_index += lsi
                muscle_groups_tested += 1
    
    # Calculate composite strength index
    composite_strength = round(total_strength_index / muscle_groups_tested, 1) if muscle_groups_tested > 0 else 0
    
    # Determine strength readiness
    passed_groups = sum(1 for result in strength_results.values() if result["passed"])
    strength_pass_rate = (passed_groups / len(strength_results)) * 100 if strength_results else 0
    
    strength_cleared = composite_strength >= 90 and strength_pass_rate >= 80
    
    return {
        "muscle_group_results": strength_results,
        "composite_strength_index": composite_strength,
        "strength_pass_rate": round(strength_pass_rate, 1),
        "strength_cleared": strength_cleared,
        "muscle_groups_tested": muscle_groups_tested
    }

def calculate_agility_testing_battery(agility_data, sport_type="multidirectional"):
    """
    Sport-specific agility testing
    
    Based on: Gokeler A, et al. Sports Med. 2017;47(11):2201-2218.
    """
    
    # Sport-specific normative data
    agility_norms = {
        "multidirectional": {
            "t_test": {"male": 9.5, "female": 10.5},
            "505_test": {"male": 2.2, "female": 2.4},
            "illinois_test": {"male": 15.2, "female": 17.0}
        },
        "linear": {
            "40_yard": {"male": 4.6, "female": 5.1},
            "60_yard": {"male": 6.8, "female": 7.5}
        },
        "reactive": {
            "reactive_agility": {"male": 1.8, "female": 2.0}
        }
    }
    
    norms = agility_norms.get(sport_type, agility_norms["multidirectional"])
    
    agility_results = {}
    tests_passed = 0
    total_tests = 0
    
    for test_name, gender_norms in norms.items():
        if test_name in agility_data:
            result = agility_data[test_name]
            gender = agility_data.get("gender", "male")
            
            norm_time = gender_norms.get(gender, gender_norms["male"])
            
            # Calculate percentage of norm (lower time = better performance)
            percentage_norm = (norm_time / result) * 100 if result > 0 else 0
            passed = percentage_norm >= 95  # Within 5% of norm
            
            agility_results[test_name] = {
                "result_time": result,
                "norm_time": norm_time,
                "percentage_norm": round(percentage_norm, 1),
                "passed": passed
            }
            
            if passed:
                tests_passed += 1
            total_tests += 1
    
    agility_pass_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    agility_cleared = agility_pass_rate >= 80
    
    return {
        "agility_results": agility_results,
        "agility_pass_rate": round(agility_pass_rate, 1),
        "agility_cleared": agility_cleared,
        "sport_type": sport_type
    }

def comprehensive_rts_assessment(hop_results, strength_results, agility_results, 
                                psychological_data, injury_history):
    """
    Comprehensive RTS decision algorithm
    
    Based on: Ardern CL, et al. Br J Sports Med. 2016;50(19):1179-1187.
    """
    
    # Weight factors for different components
    weights = {
        "hop_tests": 0.30,
        "strength": 0.25,
        "agility": 0.20,
        "psychological": 0.15,
        "injury_factors": 0.10
    }
    
    # Calculate component scores (0-100)
    hop_score = hop_results.get("composite_lsi", 0)
    strength_score = strength_results.get("composite_strength_index", 0)
    agility_score = agility_results.get("agility_pass_rate", 0)
    
    # Psychological readiness score
    psych_factors = {
        "confidence": psychological_data.get("confidence_score", 50),  # 0-100
        "fear_avoidance": 100 - psychological_data.get("fear_score", 50),  # Reverse scored
        "motivation": psychological_data.get("motivation_score", 50)
    }
    psych_score = sum(psych_factors.values()) / len(psych_factors)
    
    # Injury history factors
    injury_factors = {
        "time_since_injury": min(100, injury_history.get("months_since_injury", 0) * 10),
        "previous_injuries": max(0, 100 - injury_history.get("previous_injury_count", 0) * 20),
        "compliance": injury_history.get("rehab_compliance", 80)
    }
    injury_score = sum(injury_factors.values()) / len(injury_factors)
    
    # Calculate weighted composite score
    composite_score = (
        hop_score * weights["hop_tests"] +
        strength_score * weights["strength"] +
        agility_score * weights["agility"] +
        psych_score * weights["psychological"] +
        injury_score * weights["injury_factors"]
    )
    
    # Determine RTS recommendation
    if composite_score >= 90:
        rts_recommendation = "CLEARED"
        risk_category = "Low Risk"
        timeline = "Immediate return to sport"
        color = "green"
    elif composite_score >= 80:
        rts_recommendation = "CONDITIONAL"
        risk_category = "Low-Moderate Risk"
        timeline = "Return with sport-specific progression"
        color = "yellow"
    elif composite_score >= 70:
        rts_recommendation = "NOT READY"
        risk_category = "Moderate Risk"
        timeline = "2-4 weeks additional training"
        color = "orange"
    else:
        rts_recommendation = "NOT CLEARED"
        risk_category = "High Risk"
        timeline = "6-8 weeks comprehensive rehabilitation"
        color = "red"
    
    # Identify limiting factors
    component_scores = {
        "Hop Tests": hop_score,
        "Strength": strength_score,
        "Agility": agility_score,
        "Psychological": psych_score,
        "Injury Factors": injury_score
    }
    
    limiting_factors = [
        component for component, score in component_scores.items() 
        if score < 85
    ]
    
    return {
        "composite_score": round(composite_score, 1),
        "rts_recommendation": rts_recommendation,
        "risk_category": risk_category,
        "timeline": timeline,
        "color": color,
        "component_scores": {k: round(v, 1) for k, v in component_scores.items()},
        "limiting_factors": limiting_factors,
        "specific_recommendations": generate_rts_recommendations(limiting_factors, component_scores),
        "assessment_date": datetime.now().strftime("%Y-%m-%d")
    }

def generate_rts_recommendations(limiting_factors, scores):
    """Generate specific recommendations based on limiting factors"""
    
    recommendations = []
    
    if "Hop Tests" in limiting_factors:
        recommendations.append({
            "area": "Functional Performance",
            "recommendation": "Focus on plyometric training and single-limb exercises",
            "timeline": "2-4 weeks",
            "exercises": ["Single leg hops", "Lateral bounds", "Depth jumps"]
        })
    
    if "Strength" in limiting_factors:
        recommendations.append({
            "area": "Strength Training",
            "recommendation": "Intensive strength training targeting weak muscle groups",
            "timeline": "4-6 weeks", 
            "exercises": ["Eccentric strengthening", "Progressive resistance", "Isokinetic training"]
        })
    
    if "Agility" in limiting_factors:
        recommendations.append({
            "area": "Movement Quality",
            "recommendation": "Sport-specific agility and cutting drills",
            "timeline": "2-3 weeks",
            "exercises": ["Cone drills", "Reactive agility", "Sport-specific movements"]
        })
    
    if "Psychological" in limiting_factors:
        recommendations.append({
            "area": "Psychological Readiness",
            "recommendation": "Address fear-avoidance and build confidence",
            "timeline": "Ongoing",
            "exercises": ["Graded exposure", "Visualization", "Sport psychology support"]
        })
    
    return recommendations

def create_rts_report(assessment_data):
    """Generate comprehensive RTS assessment report"""
    
    report = {
        "patient_info": assessment_data.get("patient_info", {}),
        "assessment_summary": assessment_data.get("comprehensive_assessment", {}),
        "detailed_results": {
            "hop_testing": assessment_data.get("hop_results", {}),
            "strength_testing": assessment_data.get("strength_results", {}),
            "agility_testing": assessment_data.get("agility_results", {})
        },
        "recommendations": assessment_data.get("comprehensive_assessment", {}).get("specific_recommendations", []),
        "follow_up_plan": generate_follow_up_plan(assessment_data),
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "next_assessment": calculate_next_assessment_date(assessment_data)
    }
    
    return report

def generate_follow_up_plan(assessment_data):
    """Generate follow-up plan based on RTS results"""
    
    rts_status = assessment_data.get("comprehensive_assessment", {}).get("rts_recommendation", "NOT READY")
    
    if rts_status == "CLEARED":
        return {
            "timeline": "2 weeks post-RTS",
            "focus": "Monitor for any issues with return to sport",
            "assessments": ["Functional screening", "Symptom monitoring"]
        }
    elif rts_status == "CONDITIONAL":
        return {
            "timeline": "1 week",
            "focus": "Progressive return with monitoring",
            "assessments": ["Weekly functional tests", "Load monitoring"]
        }
    else:
        return {
            "timeline": "2-4 weeks", 
            "focus": "Address limiting factors identified",
            "assessments": ["Repeat testing battery", "Progress evaluation"]
        }

def calculate_next_assessment_date(assessment_data):
    """Calculate when next assessment should occur"""
    
    from datetime import datetime, timedelta
    
    rts_status = assessment_data.get("comprehensive_assessment", {}).get("rts_recommendation", "NOT READY")
    
    if rts_status == "CLEARED":
        weeks_ahead = 8  # Post-RTS follow-up
    elif rts_status == "CONDITIONAL":
        weeks_ahead = 2  # Close monitoring
    elif rts_status == "NOT READY":
        weeks_ahead = 4  # Retest after training
    else:
        weeks_ahead = 6  # Comprehensive rehab needed
    
    next_date = datetime.now() + timedelta(weeks=weeks_ahead)
    return next_date.strftime("%Y-%m-%d")