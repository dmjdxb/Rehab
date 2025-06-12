import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Import Phase 2 modules
try:
    from rts_testing import (
        calculate_hop_test_battery, calculate_strength_testing_battery,
        calculate_agility_testing_battery, comprehensive_rts_assessment
    )
    from recovery_predictions import (
        predict_recovery_timeline, generate_timeline_recommendations,
        track_recovery_progress
    )
    from contraindication_checker import (
        check_exercise_contraindications, create_safety_checklist,
        monitor_exercise_response
    )
    from treatment_plan_templates import (
        generate_treatment_plan, export_treatment_plan
    )
except ImportError:
    st.error("⚠️ Phase 2 modules not found. Please add the required Python files.")
    st.stop()

st.title("🏥 Clinical Game-Changers")
st.markdown("**Phase 2:** Advanced clinical decision support tools for elite rehabilitation")

# Create tabs for the 4 main features
tab1, tab2, tab3, tab4 = st.tabs([
    "🏃‍♂️ Return-to-Sport Testing",
    "📅 Recovery Predictions", 
    "⚠️ Exercise Safety",
    "📋 Treatment Plans"
])

# Tab 1: Return-to-Sport Testing
with tab1:
    st.header("🏃‍♂️ Return-to-Sport Testing Battery")
    st.markdown("*Evidence-based protocols for determining readiness to return to sport*")
    
    # Patient and injury information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Patient Information")
        patient_name = st.text_input("Patient Name")
        injury_type = st.selectbox("Injury Type", ["ACL", "Achilles", "Hamstring", "MCL", "PCL"])
        sport_level = st.selectbox("Sport Level", ["recreational", "competitive", "elite"])
        months_post_injury = st.number_input("Months Post-Injury", 0, 24, 6)
    
    with col2:
        st.subheader("🧠 Psychological Readiness")
        confidence_score = st.slider("Confidence in Injured Limb (0-100)", 0, 100, 70)
        fear_score = st.slider("Fear of Re-injury (0-100)", 0, 100, 30)
        motivation_score = st.slider("Motivation to Return (0-100)", 0, 100, 80)
    
    # Hop Testing Section
    st.subheader("🦘 Hop Test Battery")
    st.caption("Enter distances in centimeters or times in seconds")
    
    hop_col1, hop_col2 = st.columns(2)
    
    with hop_col1:
        st.write("**Injured Limb Results:**")
        single_hop_injured = st.number_input("Single Hop Distance (cm)", 0.0, 300.0, 0.0, key="single_injured")
        triple_hop_injured = st.number_input("Triple Hop Distance (cm)", 0.0, 800.0, 0.0, key="triple_injured")
        crossover_hop_injured = st.number_input("Crossover Hop Distance (cm)", 0.0, 800.0, 0.0, key="cross_injured")
        timed_hop_injured = st.number_input("6m Timed Hop (seconds)", 0.0, 10.0, 0.0, key="timed_injured")
    
    with hop_col2:
        st.write("**Uninjured Limb Results:**")
        single_hop_uninjured = st.number_input("Single Hop Distance (cm)", 0.0, 300.0, 0.0, key="single_uninjured")
        triple_hop_uninjured = st.number_input("Triple Hop Distance (cm)", 0.0, 800.0, 0.0, key="triple_uninjured")
        crossover_hop_uninjured = st.number_input("Crossover Hop Distance (cm)", 0.0, 800.0, 0.0, key="cross_uninjured")
        timed_hop_uninjured = st.number_input("6m Timed Hop (seconds)", 0.0, 10.0, 0.0, key="timed_uninjured")
    
    # Strength Testing Section
    st.subheader("💪 Strength Testing")
    
    strength_col1, strength_col2 = st.columns(2)
    
    with strength_col1:
        st.write("**Injured Limb (Nm):**")
        knee_ext_injured = st.number_input("Knee Extension", 0.0, 500.0, 0.0, key="ext_injured")
        knee_flex_injured = st.number_input("Knee Flexion", 0.0, 500.0, 0.0, key="flex_injured")
    
    with strength_col2:
        st.write("**Uninjured Limb (Nm):**")
        knee_ext_uninjured = st.number_input("Knee Extension", 0.0, 500.0, 0.0, key="ext_uninjured")
        knee_flex_uninjured = st.number_input("Knee Flexion", 0.0, 500.0, 0.0, key="flex_uninjured")
    
    # Calculate RTS Assessment
    if st.button("🎯 Calculate Return-to-Sport Readiness", use_container_width=True):
        # Prepare data
        hop_data = {
            "single_hop_injured": single_hop_injured,
            "single_hop_uninjured": single_hop_uninjured,
            "triple_hop_injured": triple_hop_injured,
            "triple_hop_uninjured": triple_hop_uninjured,
            "crossover_hop_injured": crossover_hop_injured,
            "crossover_hop_uninjured": crossover_hop_uninjured,
            "timed_hop_injured": timed_hop_injured,
            "timed_hop_uninjured": timed_hop_uninjured
        }
        
        strength_data = {
            "knee_extension_injured": knee_ext_injured,
            "knee_extension_uninjured": knee_ext_uninjured,
            "knee_flexion_injured": knee_flex_injured,
            "knee_flexion_uninjured": knee_flex_uninjured
        }
        
        psychological_data = {
            "confidence_score": confidence_score,
            "fear_score": fear_score,
            "motivation_score": motivation_score
        }
        
        injury_history = {
            "months_since_injury": months_post_injury,
            "previous_injury_count": 0,
            "rehab_compliance": 85
        }
        
        # Calculate assessments
        hop_results = calculate_hop_test_battery(hop_data, injury_type, sport_level)
        strength_results = calculate_strength_testing_battery(strength_data, injury_type)
        
        # Mock agility data for demo
        agility_data = {"t_test": 9.8, "gender": "male"}
        agility_results = calculate_agility_testing_battery(agility_data)
        
        comprehensive_results = comprehensive_rts_assessment(
            hop_results, strength_results, agility_results, 
            psychological_data, injury_history
        )
        
        # Display Results
        st.markdown("---")
        st.subheader("🎯 Return-to-Sport Assessment Results")
        
        # Overall Result with Color Coding
        result_color = comprehensive_results["color"]
        colors = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴"}
        color_icon = colors.get(result_color, "⚪")
        
        st.markdown(f"## {color_icon} **{comprehensive_results['rts_recommendation']}**")
        st.markdown(f"**Risk Category:** {comprehensive_results['risk_category']}")
        st.markdown(f"**Timeline:** {comprehensive_results['timeline']}")
        
        # Component Scores
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Composite Score", f"{comprehensive_results['composite_score']}/100")
        with col2:
            st.metric("Hop Test LSI", f"{hop_results['composite_lsi']}%")
        with col3:
            st.metric("Strength LSI", f"{strength_results['composite_strength_index']}%")
        
        # Detailed Component Analysis
        fig = px.bar(
            x=list(comprehensive_results['component_scores'].keys()),
            y=list(comprehensive_results['component_scores'].values()),
            title="Component Score Breakdown",
            labels={'x': 'Assessment Area', 'y': 'Score (0-100)'}
        )
        fig.add_hline(y=85, line_dash="dash", line_color="green", annotation_text="Target (85)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Limiting Factors and Recommendations
        if comprehensive_results['limiting_factors']:
            st.subheader("⚠️ Limiting Factors")
            for factor in comprehensive_results['limiting_factors']:
                st.warning(f"• {factor}")
        
        st.subheader("📋 Specific Recommendations")
        for rec in comprehensive_results['specific_recommendations']:
            with st.expander(f"🎯 {rec['area']} - {rec['timeline']}"):
                st.write(f"**Recommendation:** {rec['recommendation']}")
                st.write(f"**Suggested Exercises:** {', '.join(rec['exercises'])}")

# Tab 2: Recovery Predictions
with tab2:
    st.header("📅 Recovery Timeline Predictions")
    st.markdown("*Evidence-based predictions for rehabilitation timelines*")
    
    # Input Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🩺 Injury Information")
        pred_injury_type = st.selectbox("Injury Type", ["ACL", "Achilles", "Hamstring", "Meniscus", "Rotator_Cuff"], key="pred_injury")
        injury_severity = st.selectbox("Severity/Grade", ["conservative", "surgical", "grade_1", "grade_2", "grade_3"])
        injury_date = st.date_input("Date of Injury", datetime.now() - timedelta(days=30))
        
    with col2:
        st.subheader("👤 Patient Factors")
        pred_age = st.number_input("Age", 15, 80, 30, key="pred_age")
        fitness_level = st.selectbox("Pre-injury Fitness", ["elite", "high", "average", "low", "sedentary"])
        compliance = st.selectbox("Expected Compliance", ["excellent", "good", "fair", "poor"])
        
    # Additional Factors
    st.subheader("🔍 Additional Factors")
    
    factor_col1, factor_col2 = st.columns(2)
    
    with factor_col1:
        comorbidities = st.multiselect("Comorbidities", ["diabetes", "smoking", "obesity", "cardiovascular", "autoimmune"])
        treatment_quality = st.selectbox("Treatment Quality", ["optimal", "good", "standard", "suboptimal"])
        
    with factor_col2:
        psychological_readiness = st.slider("Psychological Readiness (0-100)", 0, 100, 70, key="psych_ready")
        primary_goal = st.selectbox("Primary Goal", ["return_to_sport", "return_to_function", "pain_relief"])
    
    if st.button("🔮 Predict Recovery Timeline", use_container_width=True):
        # Prepare prediction data
        injury_data = {
            "injury_type": pred_injury_type,
            "severity": injury_severity,
            "treatment": injury_severity,
            "injury_date": injury_date.strftime("%Y-%m-%d")
        }
        
        patient_factors = {
            "age": pred_age,
            "fitness_level": fitness_level,
            "expected_compliance": compliance,
            "comorbidities": comorbidities,
            "psychological_readiness": psychological_readiness
        }
        
        treatment_factors = {
            "treatment_quality": treatment_quality
        }
        
        treatment_goals = {
            "primary_goal": primary_goal
        }
        
        # Generate prediction
        prediction = predict_recovery_timeline(injury_data, patient_factors, treatment_factors)
        
        # Display Results
        st.markdown("---")
        st.subheader("🔮 Recovery Timeline Prediction")
        
        # Summary Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Predicted Duration", f"{prediction['total_recovery_weeks']} weeks")
        with col2:
            st.metric("Base Timeline", f"{prediction['base_recovery_weeks']} weeks")
        with col3:
            ci = prediction['confidence_intervals']['80_percent_range']
            st.metric("80% Confidence", f"{ci['lower']}-{ci['upper']} weeks")
        with col4:
            st.metric("Prediction Accuracy", f"{prediction['prediction_accuracy']['percentage']}%")
        
        # Phase Timeline Visualization
        phases_data = []
        for phase, data in prediction['phase_timelines'].items():
            phases_data.append({
                "Phase": phase.replace("_", " ").title(),
                "Start": data['start_week'],
                "Duration": data['duration_weeks'],
                "End": data['end_week']
            })
        
        df_phases = pd.DataFrame(phases_data)
        
        fig = px.timeline(
            df_phases, 
            x_start="Start", 
            x_end="End", 
            y="Phase",
            title="Recovery Phase Timeline",
            labels={'x': 'Weeks from Injury'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Modifying Factors
        st.subheader("📊 Factors Affecting Timeline")
        modifiers = prediction['modifying_factors']
        
        factor_data = []
        for factor, value in modifiers.items():
            if factor != 'total_modifier':
                effect = "Faster" if value < 1.0 else "Slower" if value > 1.0 else "Neutral"
                factor_data.append({
                    "Factor": factor.replace("_", " ").title(),
                    "Modifier": value,
                    "Effect": effect,
                    "Impact": f"{abs(1-value)*100:.0f}%"
                })
        
        df_factors = pd.DataFrame(factor_data)
        st.dataframe(df_factors, use_container_width=True)
        
        # Timeline Optimization Recommendations
        recommendations = generate_timeline_recommendations(prediction)
        if recommendations:
            st.subheader("🎯 Timeline Optimization")
            for rec in recommendations:
                priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🔵"}
                priority_icon = priority_colors.get(rec['priority'], "📝")
                
                with st.expander(f"{priority_icon} {rec['category']} - {rec['potential_improvement']}"):
                    st.write(f"**Recommendation:** {rec['recommendation']}")
                    st.write(f"**Priority:** {rec['priority']}")

# Tab 3: Exercise Safety
with tab3:
    st.header("⚠️ Exercise Safety & Contraindications")
    st.markdown("*Comprehensive safety screening for exercise prescription*")
    
    # Patient Profile for Safety Check
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Patient Profile")
        safety_age = st.number_input("Age", 15, 90, 35, key="safety_age")
        pregnant = st.checkbox("Pregnant")
        trimester = st.selectbox("Trimester", [1, 2, 3]) if pregnant else 1
        
        # Medical History
        st.write("**Medical History:**")
        unstable_angina = st.checkbox("Unstable angina")
        uncontrolled_arrhythmia = st.checkbox("Uncontrolled arrhythmia")
        recent_cardiac_event = st.checkbox("Recent cardiac event (<6 months)")
        fever = st.checkbox("Current fever/infection")
        
    with col2:
        st.subheader("💊 Current Status")
        systolic_bp = st.number_input("Systolic BP (mmHg)", 80, 250, 120)
        blood_glucose = st.number_input("Blood Glucose (mg/dL)", 50, 400, 100)
        
        medications = st.multiselect("Current Medications", [
            "beta_blockers", "blood_thinners", "insulin", "steroids"
        ])
        
        # Current Symptoms
        current_pain = st.slider("Current Pain Level (0-10)", 0, 10, 0)
    
    # Exercise Information
    st.subheader("🏋️ Proposed Exercise")
    
    exercise_col1, exercise_col2 = st.columns(2)
    
    with exercise_col1:
        exercise_name = st.text_input("Exercise Name", "Squats")
        exercise_type = st.selectbox("Exercise Type", [
            "strength", "cardiovascular", "plyometric", "balance", "flexibility"
        ])
        exercise_intensity = st.selectbox("Intensity", ["low", "moderate", "high"])
        
    with exercise_col2:
        position = st.selectbox("Exercise Position", ["standing", "sitting", "supine", "prone", "side_lying"])
        contact_risk = st.checkbox("Risk of contact/falling")
        cognitive_demand = st.selectbox("Cognitive Demand", ["low", "moderate", "high"])
    
    # Injury-Specific Information
    st.subheader("🩹 Current Injury")
    current_injury = st.selectbox("Current Injury", ["ACL", "Achilles", "Hamstring", "Rotator_Cuff", "Concussion", "None"])
    injury_phase = st.selectbox("Injury Phase", ["early", "mid", "late"]) if current_injury != "None" else "mid"
    rom_limitation = st.slider("ROM Limitation (%)", 0, 80, 0)
    
    if st.button("🔍 Check Exercise Safety", use_container_width=True):
        # Prepare data for safety check
        patient_profile = {
            "age": safety_age,
            "pregnant": pregnant,
            "trimester": trimester,
            "unstable_angina": unstable_angina,
            "uncontrolled_arrhythmia": uncontrolled_arrhythmia,
            "recent_cardiac_event": recent_cardiac_event,
            "fever": fever,
            "systolic_bp": systolic_bp,
            "blood_glucose": blood_glucose,
            "medications": medications
        }
        
        exercise_data = {
            "name": exercise_name,
            "type": exercise_type,
            "intensity": exercise_intensity,
            "position": position,
            "contact_risk": contact_risk,
            "cognitive_demand": cognitive_demand
        }
        
        injury_data = {
            "injury_type": current_injury,
            "phase": injury_phase,
            "current_pain": current_pain,
            "rom_limitation": rom_limitation
        }
        
        # Perform safety check
        safety_results = check_exercise_contraindications(patient_profile, exercise_data, injury_data)
        
        # Display Results
        st.markdown("---")
        
        # Overall Safety Assessment
        safety_level = safety_results['safety_assessment']['level']
        safety_color = safety_results['safety_assessment']['color']
        
        safety_icons = {
            "SAFE": "🟢",
            "LOW_RISK": "🟡", 
            "MODERATE_RISK": "🟠",
            "HIGH_RISK": "🔴",
            "UNSAFE": "⛔"
        }
        
        safety_icon = safety_icons.get(safety_level, "⚪")
        
        st.markdown(f"## {safety_icon} Safety Level: {safety_level}")
        st.markdown(f"**Recommendation:** {safety_results['safety_assessment']['recommendation']}")
        
        # Contraindications
        contraindications = safety_results['contraindications']
        
        if contraindications['absolute']:
            st.error("🚨 **ABSOLUTE CONTRAINDICATIONS**")
            for contra in contraindications['absolute']:
                with st.expander(f"⛔ {contra['contraindication']}"):
                    st.write(f"**Category:** {contra['category']}")
                    st.write(f"**Action Required:** {contra['action']}")
                    st.write(f"**Evidence:** {contra['evidence']}")
        
        if contraindications['relative']:
            st.warning("⚠️ **RELATIVE CONTRAINDICATIONS**")
            for contra in contraindications['relative']:
                with st.expander(f"⚠️ {contra['contraindication']}"):
                    st.write(f"**Recommendation:** {contra['recommendation']}")
                    st.write(f"**Evidence:** {contra['evidence']}")
        
        if contraindications['precautions']:
            st.info("ℹ️ **EXERCISE PRECAUTIONS**")
            for precaution in contraindications['precautions']:
                with st.expander(f"⚠️ {precaution['precaution']}"):
                    st.write(f"**Severity:** {precaution['severity']}")
                    st.write(f"**Recommendation:** {precaution['recommendation']}")
                    if 'alternative' in precaution:
                        st.write(f"**Alternative:** {precaution['alternative']}")
        
        # Exercise Modifications
        if contraindications['modifications']:
            st.subheader("🔧 Recommended Modifications")
            for mod in contraindications['modifications']:
                st.write(f"• **{mod['type']}:** {mod['modification']}")
                st.caption(f"Rationale: {mod['rationale']}")

# Tab 4: Treatment Plans
with tab4:
    st.header("📋 Evidence-Based Treatment Plans")
    st.markdown("*Standardized, customizable treatment protocols*")
    
    # Treatment Plan Generation
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🩺 Diagnosis & Treatment")
        plan_injury = st.selectbox("Injury/Condition", ["ACL", "Hamstring", "Rotator_Cuff", "Meniscus"], key="plan_injury")
        plan_severity = st.selectbox("Severity/Approach", ["conservative", "surgical", "grade_1", "grade_2", "grade_3"], key="plan_severity")
        plan_start_date = st.date_input("Treatment Start Date", datetime.now())
        
    with col2:
        st.subheader("👤 Patient Characteristics")
        plan_age = st.number_input("Patient Age", 15, 80, 30, key="plan_age")
        plan_activity = st.selectbox("Activity Level", ["sedentary", "recreational", "competitive", "elite"], key="plan_activity")
        plan_goal = st.selectbox("Primary Treatment Goal", ["pain_relief", "return_to_function", "return_to_sport"], key="plan_goal")
    
    # Additional Patient Factors
    st.subheader("🔍 Additional Factors")
    plan_comorbidities = st.multiselect("Comorbidities", ["diabetes", "osteoporosis", "cardiovascular", "obesity"], key="plan_comorbidities")
    plan_compliance = st.selectbox("Expected Compliance", ["excellent", "good", "fair", "poor"], key="plan_compliance")
    
    if st.button("📋 Generate Treatment Plan", use_container_width=True):
        # Prepare treatment plan data
        injury_data = {
            "injury_type": plan_injury,
            "severity": plan_severity,
            "treatment_approach": plan_severity,
            "start_date": plan_start_date.strftime("%Y-%m-%d")
        }
        
        patient_profile = {
            "age": plan_age,
            "activity_level": plan_activity,
            "comorbidities": plan_comorbidities,
            "expected_compliance": plan_compliance,
            "name": "Patient"
        }
        
        treatment_goals = {
            "primary_goal": plan_goal
        }
        
        # Generate treatment plan
        treatment_plan = generate_treatment_plan(injury_data, patient_profile, treatment_goals)
        
        # Display Treatment Plan
        st.markdown("---")
        st.subheader("📋 Generated Treatment Plan")
        
        # Plan Overview
        plan_data = treatment_plan['treatment_plan']
        timeline_data = treatment_plan['timeline']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Duration", f"{plan_data['duration_weeks']} weeks")
        with col2:
            st.metric("Number of Phases", len(plan_data['phases']))
        with col3:
            st.metric("Start Date", timeline_data['start_date'])
        
        # Phase Timeline
        st.subheader("📅 Treatment Timeline")
        
        timeline_phases = []
        for phase_name, phase_timeline in timeline_data['phases'].items():
            timeline_phases.append({
                "Phase": phase_name.replace("_", " ").title(),
                "Start Date": phase_timeline['start_date'],
                "End Date": phase_timeline['end_date'],
                "Duration (weeks)": phase_timeline['duration_weeks'],
                "Key Goals": ", ".join(phase_timeline['goals'][:2])  # First 2 goals
            })
        
        df_timeline = pd.DataFrame(timeline_phases)
        st.dataframe(df_timeline, use_container_width=True)
        
        # Detailed Phase Information
        st.subheader("📖 Phase Details")
        
        for phase_name, phase_data in plan_data['phases'].items():
            with st.expander(f"📌 {phase_name.replace('_', ' ').title()} - {timeline_data['phases'][phase_name]['duration_weeks']} weeks"):
                
                phase_col1, phase_col2 = st.columns(2)
                
                with phase_col1:
                    st.write("**Goals:**")
                    for goal in phase_data.get('goals', []):
                        st.write(f"• {goal}")
                    
                    if 'criteria_to_progress' in phase_data:
                        st.write("**Progression Criteria:**")
                        for criteria in phase_data['criteria_to_progress']:
                            st.write(f"• {criteria}")
                
                with phase_col2:
                    st.write("**Key Interventions:**")
                    for intervention in phase_data.get('interventions', [])[:5]:  # Top 5
                        st.write(f"• {intervention}")
                    
                    if 'precautions' in phase_data:
                        st.write("**Precautions:**")
                        for precaution in phase_data['precautions']:
                            st.write(f"⚠️ {precaution}")
        
        # Milestones
        if 'milestones' in timeline_data:
            st.subheader("🎯 Key Milestones")
            
            milestone_data = []
            for milestone_name, milestone_info in timeline_data['milestones'].items():
                milestone_data.append({
                    "Milestone": milestone_name.replace("_", " ").title(),
                    "Target Date": milestone_info['target_date'],
                    "Description": milestone_info['description'],
                    "Assessment": milestone_info.get('assessment', 'Clinical evaluation')
                })
            
            df_milestones = pd.DataFrame(milestone_data)
            st.dataframe(df_milestones, use_container_width=True)
        
        # Documentation and Export
        st.subheader("📄 Documentation")
        
        doc_data = treatment_plan['documentation']
        
        st.write("**Recommended Outcome Measures:**")
        for measure in doc_data['outcome_measures']['baseline_assessment']:
            st.write(f"• {measure}")
        
        st.write("**Follow-up Schedule:**")
        st.write(f"• Reassessments: {doc_data['outcome_measures']['reassessment_frequency']}")
        
        # Export Options
        st.subheader("📤 Export Options")
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("📄 Export as PDF", use_container_width=True):
                export_result = export_treatment_plan(treatment_plan, "pdf")
                st.success(f"✅ Plan exported: {export_result['file_name']}")
        
        with export_col2:
            if st.button("📊 Export as Excel", use_container_width=True):
                export_result = export_treatment_plan(treatment_plan, "xlsx")
                st.success(f"✅ Plan exported: {export_result['file_name']}")

# Add instructions and evidence base
st.markdown("---")
st.markdown("""
### 📚 **Evidence Base for Phase 2 Features:**

**🏃‍♂️ Return-to-Sport Testing:**
- Hop test LSI thresholds (Reid et al., 2007; Gokeler et al., 2017)
- Strength testing protocols (Schmitt et al., 2012)
- Psychological readiness assessment (Ardern et al., 2016)

**📅 Recovery Predictions:**
- Tissue healing timelines (van der Horst et al., 2015)
- Prognostic factor research (Ardern et al., 2014)
- Patient-specific modeling approaches

**⚠️ Exercise Safety:**
- ACSM Exercise Testing Guidelines (2022)
- Injury-specific contraindications
- Clinical red flag screening protocols

**📋 Treatment Plans:**
- Clinical practice guidelines
- Evidence-based rehabilitation protocols
- Systematic review recommendations

All algorithms include **confidence intervals** and **prediction accuracy** metrics for clinical decision-making.
""")

st.info("💡 **Integration:** These tools work seamlessly with your existing rehab engine and outcome measures for comprehensive patient care.")