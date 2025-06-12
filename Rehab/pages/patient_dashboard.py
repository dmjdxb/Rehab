# Updated patient_dashboard.py with full patient integration

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

# Import the patient session manager
from patient_session_manager import PatientSessionManager

# Page config
st.set_page_config(page_title="Patient Dashboard", page_icon="📊", layout="wide")
st.title("📊 Patient Dashboard")

# Initialize patient session manager
PatientSessionManager.init_session_state()

# Patient selector
patient_id = PatientSessionManager.create_patient_selector(key="dashboard_patient_selector")

if not patient_id:
    st.warning("Please select a patient to view their dashboard.")
    
    # Show option to go to patient management
    if st.button("Go to Patient Management"):
        st.switch_page("pages/patient_management.py")
    st.stop()

# Get patient data
patient = PatientSessionManager.get_current_patient()
patient_name = st.session_state.current_patient_name

# Load session data for this patient
session_df = PatientSessionManager.get_patient_sessions()

if len(session_df) == 0:
    st.warning(f"No session data found for {patient_name}.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏃‍♂️ Start First Assessment"):
            st.switch_page("pages/rehab_engine.py")
    with col2:
        if st.button("📝 Add Manual Entry"):
            st.info("Manual entry feature coming soon!")
    
    st.stop()

# Data preparation
session_df['Date'] = pd.to_datetime(session_df['Date'])
session_df = session_df.sort_values('Date')

st.success(f"✅ Loaded {len(session_df)} sessions for {patient_name}")

# Patient summary header
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    age = PatientSessionManager.calculate_age(patient['DateOfBirth'])
    st.metric("Age", f"{age} years")

with col2:
    st.metric("Injury", patient['InjuryType'])

with col3:
    days_since_injury = (datetime.now() - pd.to_datetime(patient['InjuryDate'])).days
    st.metric("Days Since Injury", days_since_injury)

with col4:
    if pd.notna(patient.get('SurgeryDate')):
        days_post_op = (datetime.now() - pd.to_datetime(patient['SurgeryDate'])).days
        st.metric("Days Post-Op", days_post_op)
    else:
        st.metric("Surgery", "Non-operative")

with col5:
    st.metric("Current Phase", patient['CurrentPhase'])

st.markdown("---")

# Progress Overview
st.subheader("📈 Progress Overview")

# Check if we have enough data for progress tracking
if len(session_df) >= 2:
    # Create progress charts
    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        # LSI Progress Chart
        fig_lsi = px.line(session_df, x='Date', y='Symmetry Index',
                         title='Limb Symmetry Index Progress',
                         markers=True)
        
        # Add target line
        fig_lsi.add_hline(y=90, line_dash="dash", line_color="green",
                         annotation_text="Target LSI (90%)")
        
        # Add phase-specific targets
        if patient['CurrentPhase'] in ['Early (2-6 weeks)', 'Acute (0-2 weeks)']:
            fig_lsi.add_hline(y=70, line_dash="dot", line_color="orange",
                             annotation_text="Phase Goal (70%)")
        elif patient['CurrentPhase'] == 'Mid (6-12 weeks)':
            fig_lsi.add_hline(y=80, line_dash="dot", line_color="orange",
                             annotation_text="Phase Goal (80%)")
        
        fig_lsi.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_lsi, use_container_width=True)
    
    with fig_col2:
        # Pain Score Chart
        fig_pain = px.line(session_df, x='Date', y='Pain Score',
                          title='Pain Score Progress',
                          markers=True, color_discrete_sequence=['red'])
        fig_pain.update_layout(yaxis_range=[0, 10])
        fig_pain.add_hline(y=3, line_dash="dash", line_color="orange",
                          annotation_text="Acceptable Pain")
        st.plotly_chart(fig_pain, use_container_width=True)
    
    # RFD and Peak Force
    fig_col3, fig_col4 = st.columns(2)
    
    with fig_col3:
        fig_rfd = px.line(session_df, x='Date', y='RFD',
                         title='Rate of Force Development (%)',
                         markers=True, color_discrete_sequence=['purple'])
        st.plotly_chart(fig_rfd, use_container_width=True)
    
    with fig_col4:
        fig_force = px.line(session_df, x='Date', y='Peak Force',
                           title='Peak Force (N)',
                           markers=True, color_discrete_sequence=['orange'])
        st.plotly_chart(fig_force, use_container_width=True)

    # Progress Summary Metrics
    st.subheader("📊 Progress Summary")
    
    first_session = session_df.iloc[0]
    latest_session = session_df.iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        lsi_change = latest_session['Symmetry Index'] - first_session['Symmetry Index']
        st.metric("LSI Change", f"{lsi_change:+.1f}%", 
                 delta=f"{lsi_change:+.1f}%",
                 delta_color="normal" if lsi_change > 0 else "inverse")
    
    with col2:
        pain_change = latest_session['Pain Score'] - first_session['Pain Score']
        st.metric("Pain Change", f"{pain_change:+.1f}", 
                 delta=f"{pain_change:+.1f}",
                 delta_color="inverse")  # Lower is better for pain
    
    with col3:
        rfd_change = latest_session['RFD'] - first_session['RFD']
        st.metric("RFD Change", f"{rfd_change:+.1f}%", 
                 delta=f"{rfd_change:+.1f}%")
    
    with col4:
        force_change = latest_session['Peak Force'] - first_session['Peak Force']
        st.metric("Force Change", f"{force_change:+.0f}N", 
                 delta=f"{force_change:+.0f}N")

else:
    st.info("Need at least 2 sessions to show progress trends. Current sessions: " + str(len(session_df)))

# Clinical Alerts based on patient-specific data
st.subheader("⚠️ Clinical Alerts")

latest = session_df.iloc[-1]
alerts = []

# Phase-specific LSI thresholds
phase_lsi_thresholds = {
    "Acute (0-2 weeks)": 60,
    "Early (2-6 weeks)": 70,
    "Mid (6-12 weeks)": 80,
    "Late (3-6 months)": 85,
    "Return to Sport (6+ months)": 90
}

expected_lsi = phase_lsi_thresholds.get(patient['CurrentPhase'], 80)

if latest['Symmetry Index'] < expected_lsi:
    alerts.append(f"🔴 LSI below expected {expected_lsi}% for {patient['CurrentPhase']} phase")
elif latest['Symmetry Index'] >= 90:
    alerts.append("🟢 Excellent LSI - meeting return to sport criteria")

if latest['Pain Score'] > 5:
    alerts.append("🔴 High pain score - consider clinical review")
elif latest['Pain Score'] > 3:
    alerts.append("🟡 Moderate pain - monitor progression")

# Check progression rate
if len(session_df) >= 3:
    recent_sessions = session_df.tail(3)
    lsi_trend = recent_sessions['Symmetry Index'].diff().mean()
    
    if lsi_trend < 0:
        alerts.append("🟡 LSI trending downward - assess training load")
    elif lsi_trend > 5:
        alerts.append("🟢 Excellent progress rate")

# Display alerts
if alerts:
    for alert in alerts:
        if "🔴" in alert:
            st.error(alert)
        elif "🟡" in alert:
            st.warning(alert)
        else:
            st.success(alert)
else:
    st.success("✅ No clinical alerts - patient progressing well")

# Patient Goals Progress
if patient.get('Goals'):
    st.subheader("🎯 Progress Toward Goals")
    st.info(f"**Patient Goals:** {patient['Goals']}")
    
    # Goal-specific metrics
    if "return to sport" in patient['Goals'].lower():
        progress = (latest['Symmetry Index'] / 90) * 100
        st.progress(min(progress / 100, 1.0))
        st.write(f"Return to Sport Readiness: {progress:.0f}%")

# Session Details Table
st.subheader("📋 Session History")

# Display options
display_cols = st.multiselect(
    "Select columns to display:",
    options=['Date', 'Phase', 'Peak Force', 'Left Limb', 'Right Limb', 
             'Symmetry Index', 'RFD', 'Pain Score', 'Notes'],
    default=['Date', 'Phase', 'Symmetry Index', 'Pain Score', 'Notes']
)

if display_cols:
    display_df = session_df[display_cols].copy()
    
    if 'Date' in display_cols:
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(display_df.sort_values('Date', ascending=False), use_container_width=True)

# Action Buttons
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏃‍♂️ New Assessment", type="primary"):
        st.switch_page("pages/rehab_engine.py")

with col2:
    if st.button("📊 Clinical Assessments"):
        st.switch_page("pages/clinical_assessments.py")

with col3:
    if st.button("💪 Exercise Library"):
        st.switch_page("pages/advanced_search.py")

with col4:
    if st.button("📁 Export Report"):
        # Create comprehensive report
        report_data = {
            "Patient Information": {
                "Name": patient_name,
                "Age": age,
                "Injury": patient['InjuryType'],
                "Days Since Injury": days_since_injury,
                "Current Phase": patient['CurrentPhase']
            },
            "Latest Metrics": {
                "LSI": f"{latest['Symmetry Index']:.1f}%",
                "Pain Score": f"{latest['Pain Score']}/10",
                "Peak Force": f"{latest['Peak Force']}N",
                "Sessions Completed": len(session_df)
            },
            "Progress": {
                "LSI Change": f"{lsi_change:+.1f}%",
                "Pain Change": f"{pain_change:+.1f}",
                "Force Change": f"{force_change:+.0f}N"
            }
        }
        
        # Convert to downloadable format
        report_text = f"Patient Progress Report\n"
        report_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        for section, data in report_data.items():
            report_text += f"{section}:\n"
            for key, value in data.items():
                report_text += f"  {key}: {value}\n"
            report_text += "\n"
        
        st.download_button(
            label="💾 Download Report",
            data=report_text,
            file_name=f"patient_report_{patient_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )