"""
Evidence-Based Load Progression Algorithms
Scientific methods for progressing exercise intensity, volume, and complexity
"""

import math
from datetime import datetime, timedelta

def calculate_1rm_estimate(weight, reps, formula='epley'):
    """
    Estimate 1RM using validated formulas
    
    Based on: Epley B. Poundage Chart. Boyd Epley Workout. Lincoln, NE: NEP; 1985.
             Brzycki M. Strength & Health. 1993;1(1):36-40.
    """
    
    if reps == 1:
        return weight
    
    formulas = {
        'epley': weight * (1 + reps/30),
        'brzycki': weight * (36/(37-reps)),
        'lander': weight * (100/(101.3 - 2.67123*reps)),
        'lombardi': weight * (reps**0.10),
        'mayhew': weight * (100/(52.2 + 41.9*math.exp(-0.055*reps)))
    }
    
    return round(formulas.get(formula, formulas['epley']), 1)

def calculate_training_loads(one_rm, training_goal):
    """
    Calculate training loads based on % 1RM for different goals
    
    Based on: ACSM's Guidelines for Exercise Testing and Prescription. 10th ed.
              Baechle TR, Earle RW. Essentials of Strength Training. 4th ed.
    """
    
    load_prescriptions = {
        'strength': {
            'intensity_range': (85, 100),
            'reps_range': (1, 6),
            'sets_range': (3, 6),
            'rest_time': '3-5 minutes',
            'frequency': '2-3x/week',
            'progression': '2-10% when target reps achieved'
        },
        'hypertrophy': {
            'intensity_range': (67, 85),
            'reps_range': (6, 12),
            'sets_range': (3, 6),
            'rest_time': '30-90 seconds',
            'frequency': '2-3x/week',
            'progression': '2-5% when target reps achieved'
        },
        'power': {
            'intensity_range': (75, 95),
            'reps_range': (1, 5),
            'sets_range': (3, 5),
            'rest_time': '2-5 minutes',
            'frequency': '3x/week',
            'progression': 'Focus on speed of movement, then load'
        },
        'endurance': {
            'intensity_range': (50, 67),
            'reps_range': (12, 20),
            'sets_range': (2, 3),
            'rest_time': '30 seconds',
            'frequency': '3-4x/week',
            'progression': 'Increase reps first, then load'
        },
        'rehab_early': {
            'intensity_range': (40, 60),
            'reps_range': (10, 15),
            'sets_range': (2, 3),
            'rest_time': '60-90 seconds',
            'frequency': '3-5x/week',
            'progression': 'Pain-free range, then reps, then load'
        },
        'rehab_late': {
            'intensity_range': (60, 80),
            'reps_range': (8, 12),
            'sets_range': (3, 4),
            'rest_time': '90-120 seconds',
            'frequency': '3-4x/week',
            'progression': '5% increases when form maintained'
        }
    }
    
    prescription = load_prescriptions.get(training_goal, load_prescriptions['rehab_early'])
    
    # Calculate specific loads
    min_intensity, max_intensity = prescription['intensity_range']
    min_load = round(one_rm * (min_intensity/100), 1)
    max_load = round(one_rm * (max_intensity/100), 1)
    
    return {
        'training_goal': training_goal,
        'one_rm_estimate': one_rm,
        'load_range': (min_load, max_load),
        'intensity_percent': prescription['intensity_range'],
        'reps_range': prescription['reps_range'],
        'sets_range': prescription['sets_range'],
        'rest_time': prescription['rest_time'],
        'frequency': prescription['frequency'],
        'progression_strategy': prescription['progression']
    }

def calculate_rpe_loads(current_weight, current_rpe, target_rpe, exercise_type='compound'):
    """
    Calculate load adjustments based on RPE (Rate of Perceived Exertion)
    
    Based on: Zourdos MC, et al. J Strength Cond Res. 2016;30(1):267-275.
              Helms ER, et al. Sports Med. 2016;46(11):1597-1614.
    """
    
    # RPE to % 1RM relationships (research-based)
    rpe_percentages = {
        10: 100,  # Maximum effort
        9.5: 97,
        9: 94,
        8.5: 91,
        8: 88,
        7.5: 85,
        7: 82,
        6.5: 79,
        6: 76,
        5.5: 73,
        5: 70
    }
    
    # Exercise type modifiers
    exercise_modifiers = {
        'compound': 1.0,      # Squat, deadlift, bench press
        'isolation': 0.95,    # Bicep curls, leg extensions
        'unilateral': 0.90,   # Single leg, single arm exercises
        'balance': 0.85,      # Unstable surface exercises
        'functional': 0.88    # Multi-planar movements
    }
    
    modifier = exercise_modifiers.get(exercise_type, 1.0)
    
    current_percentage = rpe_percentages.get(current_rpe, 70)
    target_percentage = rpe_percentages.get(target_rpe, 70)
    
    # Estimate current 1RM
    estimated_1rm = current_weight / (current_percentage/100) * modifier
    
    # Calculate target weight
    target_weight = estimated_1rm * (target_percentage/100) * modifier
    
    # Calculate percentage change
    percentage_change = ((target_weight - current_weight) / current_weight) * 100
    
    return {
        'current_weight': current_weight,
        'current_rpe': current_rpe,
        'target_rpe': target_rpe,
        'recommended_weight': round(target_weight, 1),
        'estimated_1rm': round(estimated_1rm, 1),
        'percentage_change': round(percentage_change, 1),
        'exercise_modifier': modifier,
        'progression_notes': generate_rpe_notes(current_rpe, target_rpe, percentage_change)
    }

def generate_rpe_notes(current_rpe, target_rpe, change):
    """Generate progression guidance based on RPE changes"""
    
    if target_rpe > current_rpe:
        if change > 15:
            return "Large increase suggested - progress gradually over 2-3 sessions"
        elif change > 10:
            return "Moderate increase - monitor form and technique closely"
        else:
            return "Appropriate progression - advance when ready"
    elif target_rpe < current_rpe:
        return "Deload recommended - focus on movement quality and recovery"
    else:
        return "Maintain current load - consider volume or frequency changes"

def calculate_volume_progression(current_sets, current_reps, progression_type, weeks_training):
    """
    Calculate volume progression based on training phase and experience
    
    Based on: Rhea MR, et al. J Strength Cond Res. 2003;17(4):725-729.
    """
    
    progression_strategies = {
        'linear': {
            'weekly_increase': 2.5,  # % per week
            'max_increase': 10,      # % per session
            'deload_frequency': 4    # weeks
        },
        'step_loading': {
            'weekly_increase': 5,
            'max_increase': 15,
            'deload_frequency': 3
        },
        'undulating': {
            'weekly_increase': 3,
            'max_increase': 20,
            'deload_frequency': 4
        },
        'block': {
            'weekly_increase': 4,
            'max_increase': 12,
            'deload_frequency': 3
        }
    }
    
    strategy = progression_strategies.get(progression_type, progression_strategies['linear'])
    
    # Calculate if deload week
    is_deload_week = (weeks_training % strategy['deload_frequency']) == 0
    
    if is_deload_week:
        # Deload: reduce volume by 40-60%
        deload_factor = 0.6
        new_sets = max(1, round(current_sets * deload_factor))
        new_reps = max(5, round(current_reps * deload_factor))
        notes = "Deload week - reduce volume for recovery"
    else:
        # Progressive overload
        volume_increase = min(strategy['weekly_increase'], strategy['max_increase'])
        
        # Prioritize reps first, then sets (for most goals)
        if current_reps < 12:
            new_reps = min(15, current_reps + 1)
            new_sets = current_sets
            notes = f"Increase reps by 1 ({volume_increase:.1f}% volume increase)"
        else:
            new_reps = max(8, current_reps - 2)  # Reset reps
            new_sets = current_sets + 1
            notes = f"Add 1 set, reset reps ({volume_increase:.1f}% volume increase)"
    
    current_volume = current_sets * current_reps
    new_volume = new_sets * new_reps
    volume_change = ((new_volume - current_volume) / current_volume) * 100
    
    return {
        'current_volume': current_volume,
        'new_sets': new_sets,
        'new_reps': new_reps,
        'new_volume': new_volume,
        'volume_change_percent': round(volume_change, 1),
        'is_deload_week': is_deload_week,
        'progression_notes': notes,
        'weeks_in_program': weeks_training
    }

def generate_periodization_plan(goal, duration_weeks, current_fitness_level):
    """
    Generate a periodized training plan
    
    Based on: Issurin VB. Sports Med. 2010;40(3):189-206.
    """
    
    phases = {
        'anatomical_adaptation': {
            'duration_percent': 25,
            'intensity': 'rehab_early',
            'focus': 'Movement quality, tissue adaptation',
            'load_progression': 'linear'
        },
        'hypertrophy': {
            'duration_percent': 30,
            'intensity': 'hypertrophy',
            'focus': 'Muscle growth, work capacity',
            'load_progression': 'step_loading'
        },
        'strength': {
            'duration_percent': 25,
            'intensity': 'strength',
            'focus': 'Maximal strength development',
            'load_progression': 'undulating'
        },
        'power_peak': {
            'duration_percent': 15,
            'intensity': 'power',
            'focus': 'Peak performance, sport-specific',
            'load_progression': 'block'
        },
        'recovery': {
            'duration_percent': 5,
            'intensity': 'endurance',
            'focus': 'Active recovery, maintenance',
            'load_progression': 'linear'
        }
    }
    
    # Adjust phases based on goal
    if goal == 'return_to_sport':
        phases['power_peak']['duration_percent'] = 25
        phases['strength']['duration_percent'] = 20
    elif goal == 'general_fitness':
        phases['hypertrophy']['duration_percent'] = 40
        phases['strength']['duration_percent'] = 20
        phases['power_peak']['duration_percent'] = 5
    
    plan = []
    current_week = 0
    
    for phase_name, phase_config in phases.items():
        phase_weeks = max(1, round(duration_weeks * phase_config['duration_percent'] / 100))
        
        plan.append({
            'phase': phase_name,
            'weeks': f"{current_week + 1}-{current_week + phase_weeks}",
            'duration': phase_weeks,
            'training_goal': phase_config['intensity'],
            'primary_focus': phase_config['focus'],
            'progression_method': phase_config['load_progression']
        })
        
        current_week += phase_weeks
    
    return {
        'total_duration': duration_weeks,
        'training_goal': goal,
        'fitness_level': current_fitness_level,
        'phases': plan,
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }