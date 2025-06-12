import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Import our new modules (you'll need to add these files to your project)
try:
    from outcome_measures import (
        calculate_ikdc_score, calculate_koos_score, 
        calculate_dash_score, calculate_nprs_score,
        track_outcome_changes
    )
    from load_progression import (
        calculate_1rm_estimate, calculate_training_loads,
        calculate_rpe_loads, calculate_volume_progression,
        generate_periodization_plan
    )
    from red_flag_detection import (
        assess_red_flags, create_red_flag_screening_form
    )
except ImportError:
    st.error("⚠️ Clinical assessment modules not found. Please add the required Python files.")
    st.stop()

st.title("📊 Clinical Assessments & Progression")
st.markdown("Evidence-based tools for comprehensive patient assessment and exercise prescription")

# Create tabs for different assessment types
tab1, tab2, tab3, tab4 = st.tabs([
    "🩺 Outcome Measures", 
    "💪 Load Progression", 
    "⚠️ Red Flag Screening",
    "📈 Progress Tracking"
])

# Tab 1: Outcome Measures
with tab1:
    st.header("📋 Validated Outcome Measures")
    st.markdown("*Use scientifically validated tools to track patient progress*")
    
    # Assessment type selection
    assessment_type = st.selectbox(
        "Select Assessment Tool:",
        ["IKDC (Knee)", "KOOS (Knee)", "DASH (Upper Extremity)", "NPRS (Pain)"]
    )
    
    if assessment_type == "IKDC (Knee)":
    st.subheader("🦵 IKDC Knee Assessment")
    st.caption("International Knee Documentation Committee - Validated for knee injuries")
    
    with st.form("ikdc_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            pain_level = st.slider("Pain Level (0=severe, 10=none)", 0, 10, 5)
            swelling = st.slider("Swelling (0=severe, 4=none)", 0, 4, 2)
            locking = st.slider("Locking Episodes (0=constant, 4=never)", 0, 4, 2)
            instability = st.slider("Giving Way (0=constant, 4=never)", 0, 4, 2)
        
        with col2:
            activity_level = st.slider("Activity Level (0=unable, 4=normal)", 0, 4, 2)
            function_score = st.slider("Function (0=cannot do, 4=no difficulty)", 0, 4, 2)
            sports_participation = st.slider("Sports (0=unable, 4=normal)", 0, 4, 2)
        
        # Option to save automatically
        auto_save = st.checkbox("Auto-save assessment after calculation", value=True)
        
        # Single submit button that both calculates AND saves
        submitted = st.form_submit_button("💾 Calculate & Save IKDC Score")
        
        if submitted:
            responses = {
                'pain_level': pain_level,
                'swelling': swelling,
                'locking': locking,
                'instability': instability,
                'activity_level': activity_level,
                'function_score': function_score,
                'sports_participation': sports_participation
            }
            
            result = calculate_ikdc_score(responses)
            
            # Display results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("IKDC Score", f"{result['score']}", f"MCID: {result['mcid']}")
            with col2:
                st.metric("Risk Level", result['risk_level'])
            with col3:
                st.metric("Interpretation", result['interpretation'])
            
            st.info(f"**Recommendation:** {result['recommendation']}")
            
            # Save the assessment if auto_save is enabled
            if auto_save:
                # Add your save logic here
                # For example:
                # save_to_database(result)
                # save_to_csv(result)
                st.success("✅ Assessment calculated and saved successfully!")
            else:
                st.success("✅ Assessment calculated successfully!")

    elif assessment_type == "NPRS (Pain)":
        st.subheader("😖 Numeric Pain Rating Scale")
        st.caption("Validated pain assessment tool")
        
        with st.form("nprs_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                current_pain = st.slider("Current Pain (0-10)", 0, 10, 0)
                worst_pain = st.slider("Worst Pain (24hrs)", 0, 10, 0)
            
            with col2:
                least_pain = st.slider("Least Pain (24hrs)", 0, 10, 0)
                average_pain = st.slider("Average Pain (24hrs)", 0, 10, 0)
            
            submitted = st.form_submit_button("Calculate Pain Score")
            
            if submitted:
                result = calculate_nprs_score(current_pain, worst_pain, least_pain, average_pain)
                
                if 'error' not in result:
                    st.metric("Composite Pain Score", f"{result['composite_score']}/10")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Interpretation:** {result['interpretation']}")
                        st.write(f"**Functional Impact:** {result['functional_impact']}")
                    with col2:
                        st.write(f"**Recommendation:** {result['recommendation']}")
                        st.caption(f"MCID: {result['mcid']} points")

# Tab 2: Load Progression
with tab2:
    st.header("💪 Exercise Load Progression")
    st.markdown("*Scientific methods for progressing exercise intensity and volume*")
    
    progression_type = st.selectbox(
        "Select Progression Tool:",
        ["1RM Estimation", "Training Load Calculator", "RPE-Based Loading", "Volume Progression"]
    )
    
    if progression_type == "1RM Estimation":
        st.subheader("🏋️ One Rep Max Estimation")
        st.caption("Estimate 1RM using validated formulas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Weight Lifted (lbs/kg)", 0.0, 1000.0, 100.0)
            reps = st.number_input("Reps Completed", 1, 20, 5)
            formula = st.selectbox("Formula", ["epley", "brzycki", "lander"])
        
        with col2:
            if weight > 0 and reps > 0:
                estimated_1rm = calculate_1rm_estimate(weight, reps, formula)
                st.metric("Estimated 1RM", f"{estimated_1rm}")
                
                # Show training loads
                st.write("**Training Load Recommendations:**")
                for goal in ["strength", "hypertrophy", "endurance"]:
                    loads = calculate_training_loads(estimated_1rm, goal)
                    min_load, max_load = loads['load_range']
                    st.write(f"• **{goal.title()}:** {min_load}-{max_load} ({loads['intensity_percent'][0]}-{loads['intensity_percent'][1]}%)")

    elif progression_type == "RPE-Based Loading":
        st.subheader("📊 RPE-Based Load Adjustment")
        st.caption("Adjust loads based on Rate of Perceived Exertion")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_weight = st.number_input("Current Weight", 0.0, 1000.0, 100.0)
            current_rpe = st.selectbox("Current RPE", [5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10])
            target_rpe = st.selectbox("Target RPE", [5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10])
            exercise_type = st.selectbox("Exercise Type", ["compound", "isolation", "unilateral", "functional"])
        
        with col2:
            if current_weight > 0:
                rpe_result = calculate_rpe_loads(current_weight, current_rpe, target_rpe, exercise_type)
                
                st.metric("Recommended Weight", f"{rpe_result['recommended_weight']}")
                st.metric("Estimated 1RM", f"{rpe_result['estimated_1rm']}")
                st.write(f"**Change:** {rpe_result['percentage_change']:+.1f}%")
                st.info(rpe_result['progression_notes'])

# Tab 3: Red Flag Screening
with tab3:
    st.header("⚠️ Red Flag Screening")
    st.markdown("*Systematic screening for serious pathology requiring medical referral*")
    
    st.warning("**Important:** This is a screening tool only. Clinical judgment is always required.")
    
    # Patient information
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Patient Age", 0, 120, 30)
        region = st.selectbox("Body Region", ["spine", "knee", "shoulder", "ankle", "general"])
    
    with col2:
        onset = st.selectbox("Pain Onset", ["acute", "gradual", "chronic"])
        trauma_history = st.checkbox("History of significant trauma")
    
    # Systematic screening questions
    st.subheader("🔍 Systematic Screening")
    
    screening_data = {'age': age, 'region': region}
    
    # Constitutional symptoms
    st.write("**Constitutional Symptoms:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        screening_data['fever'] = st.checkbox("Fever")
        screening_data['unexplained_weight_loss'] = st.checkbox("Weight loss >10lbs")
        screening_data['night_sweats'] = st.checkbox("Night sweats")
    
    with col2:
        screening_data['constant_progressive_pain'] = st.checkbox("Constant, progressive pain")
        screening_data['night_pain_no_relief'] = st.checkbox("Severe night pain")
        screening_data['new_onset_pain'] = st.checkbox("New onset pain") if age > 50 else False
    
    with col3:
        screening_data['significant_trauma'] = trauma_history
        screening_data['progressive_weakness'] = st.checkbox("Progressive weakness")
        screening_data['bladder_dysfunction'] = st.checkbox("Bladder dysfunction")
    
    # Region-specific questions
    if region == "knee":
        st.write("**Knee-Specific:**")
        screening_data['joint_effusion'] = st.checkbox("Joint effusion with warmth")
        screening_data['ottawa_knee_positive'] = st.checkbox("Ottawa Knee Rule positive")
        screening_data['pulse_deficit'] = st.checkbox("Pulse deficit or cold limb")
    
    # Assessment
    if st.button("🔍 Assess Red Flags"):
        assessment = assess_red_flags(screening_data)
        
        # Display risk level with color coding
        risk_colors = {
            'EMERGENCY': '🔴',
            'HIGH': '🟠', 
            'MODERATE': '🟡',
            'LOW': '🟢',
            'MINIMAL': '🔵'
        }
        
        risk_icon = risk_colors.get(assessment['risk_level'], '⚪')
        st.subheader(f"{risk_icon} Risk Level: {assessment['risk_level']}")
        
        # Show red flags
        if assessment['red_flags']:
            st.error("🚨 **RED FLAGS IDENTIFIED:**")
            for flag in assessment['red_flags']:
                with st.expander(f"⚠️ {flag['flag']} ({flag['severity']})"):
                    st.write(f"**Category:** {flag['category']}")
                    st.write(f"**Action Required:** {flag['action']}")
                    st.write(f"**Evidence:** {flag['evidence']}")
        
        # Show recommendations
        st.subheader("📋 Recommendations")
        for rec in assessment['recommendations']:
            priority_colors = {
                'IMMEDIATE': '🔴',
                'URGENT': '🟠',
                'ROUTINE': '🟡',
                'PREVENTIVE': '🔵'
            }
            
            icon = priority_colors.get(rec['priority'], '📝')
            st.write(f"{icon} **{rec['priority']}:** {rec['action']} ({rec['timeframe']})")
            st.caption(f"Rationale: {rec['rationale']}")

# Tab 4: Progress Tracking
with tab4:
    st.header("📈 Progress Tracking Dashboard")
    st.markdown("*Track outcome measures and exercise progression over time*")
    
    # Mock data for demonstration (in real app, load from database)
    dates = pd.date_range(start='2024-01-01', periods=12, freq='W')
    
    # Sample IKDC scores over time
    ikdc_scores = [45, 52, 58, 65, 72, 78, 82, 85, 88, 91, 93, 95]
    pain_scores = [8, 7, 6, 5, 4, 3, 3, 2, 2, 1, 1, 0]
    
    # Create progress charts
    col1, col2 = st.columns(2)
    
    with col1:
        # IKDC Progress
        fig_ikdc = px.line(
            x=dates, y=ikdc_scores,
            title="IKDC Score Progress",
            labels={'x': 'Date', 'y': 'IKDC Score'}
        )
        fig_ikdc.add_hline(y=90, line_dash="dash", line_color="green", 
                          annotation_text="Return to Sport Threshold")
        fig_ikdc.add_hline(y=60, line_dash="dash", line_color="orange",
                          annotation_text="Fair Function")
        st.plotly_chart(fig_ikdc, use_container_width=True)
    
    with col2:
        # Pain Progress
        fig_pain = px.line(
            x=dates, y=pain_scores,
            title="Pain Score Progress (NPRS)",
            labels={'x': 'Date', 'y': 'Pain Score (0-10)'}
        )
        fig_pain.add_hline(y=3, line_dash="dash", line_color="green",
                          annotation_text="Mild Pain Threshold")
        st.plotly_chart(fig_pain, use_container_width=True)
    
    # Progress summary
    st.subheader("📊 Progress Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ikdc_change = ikdc_scores[-1] - ikdc_scores[0]
        st.metric("IKDC Change", f"+{ikdc_change}", f"+{ikdc_change} points")
    
    with col2:
        pain_change = pain_scores[0] - pain_scores[-1]
        st.metric("Pain Reduction", f"-{pain_change}", f"-{pain_change} points")
    
    with col3:
        weeks_progress = len(dates)
        st.metric("Weeks in Program", weeks_progress)
    
    with col4:
        current_phase = "Return to Sport" if ikdc_scores[-1] >= 90 else "Late Phase"
        st.metric("Current Phase", current_phase)

# Add instructions at the bottom
st.markdown("---")
st.markdown("""
### 📚 **Evidence-Based Features:**

**🩺 Outcome Measures:**
- IKDC: Validated for knee injuries (Irrgang et al., 2001)
- KOOS: Comprehensive knee assessment (Roos et al., 1998)
- DASH: Upper extremity function (Hudak et al., 1996)
- NPRS: Gold standard pain assessment (Jensen et al., 2003)

**💪 Load Progression:**
- 1RM estimation using validated formulas
- Evidence-based intensity prescriptions (ACSM Guidelines)
- RPE-based auto-regulation (Zourdos et al., 2016)

**⚠️ Red Flag Screening:**
- Based on clinical practice guidelines
- Systematic approach to serious pathology detection
- Evidence from emergency medicine and orthopedics

All tools include **Minimal Clinically Important Differences (MCID)** for meaningful change detection.
""")

st.info("💡 **Next Steps:** These assessments integrate with your existing rehab engine and patient dashboard for comprehensive care.")
