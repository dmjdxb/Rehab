import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta


st.title("📊 Patient Dashboard")
st.markdown("Track patient progress over time with detailed analytics and visualizations.")

# Load session log data
log_path = "session_log.csv"

try:
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        
        # Data cleaning and preparation
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        st.success(f"✅ Loaded {len(df)} sessions from {df['Athlete'].nunique()} patients")
        
    else:
        st.warning("⚠️ No session data found. Sessions will appear here after using the Rehab Engine.")
        
        # Create sample data option
        if st.button("🔧 Create Sample Data for Testing"):
            sample_data = [
                {
                    "Date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
                    "Time": "10:00",
                    "Athlete": "John Smith",
                    "Injury": "ACL",
                    "Phase": "Early",
                    "Peak Force": 850,
                    "Left Limb": 400,
                    "Right Limb": 500,
                    "Symmetry Index": 80.0,
                    "RFD": 65.0,
                    "Pain Score": 3,
                    "Notes": "First assessment post-surgery"
                },
                {
                    "Date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "Time": "14:30",
                    "Athlete": "John Smith",
                    "Injury": "ACL",
                    "Phase": "Early",
                    "Peak Force": 920,
                    "Left Limb": 450,
                    "Right Limb": 520,
                    "Symmetry Index": 86.5,
                    "RFD": 72.0,
                    "Pain Score": 2,
                    "Notes": "Good improvement in strength"
                },
                {
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Time": "11:15",
                    "Athlete": "John Smith",
                    "Injury": "ACL",
                    "Phase": "Mid",
                    "Peak Force": 1050,
                    "Left Limb": 485,
                    "Right Limb": 535,
                    "Symmetry Index": 90.7,
                    "RFD": 78.0,
                    "Pain Score": 1,
                    "Notes": "Progressed to mid phase"
                }
            ]
            
            sample_df = pd.DataFrame(sample_data)
            sample_df.to_csv(log_path, index=False)
            st.success("✅ Sample data created! Please refresh the page.")
            st.stop()
        
        st.stop()
        
except Exception as e:
    st.error(f"Error loading session data: {e}")
    st.stop()

# Sidebar filtering
st.sidebar.header("📅 Filter Options")

# Patient selection
all_athletes = ['All Patients'] + sorted(df["Athlete"].dropna().unique().tolist())
selected_athlete = st.sidebar.selectbox("Select Patient", all_athletes)

# Date range filtering
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

# Injury type filter
all_injuries = ['All Injuries'] + sorted(df["Injury"].dropna().unique().tolist())
selected_injury = st.sidebar.selectbox("Filter by Injury", all_injuries)

# Apply filters
filtered = df.copy()

if selected_athlete != 'All Patients':
    filtered = filtered[filtered["Athlete"] == selected_athlete]

if selected_injury != 'All Injuries':
    filtered = filtered[filtered["Injury"] == selected_injury]

filtered = filtered[
    (filtered["Date"].dt.date >= start_date) &
    (filtered["Date"].dt.date <= end_date)
]

# Main dashboard content
if len(filtered) == 0:
    st.warning("No data matches the selected filters. Please adjust your selection.")
    st.stop()

# Summary metrics
st.subheader("📈 Summary Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sessions", len(filtered))
    
with col2:
    if selected_athlete != 'All Patients':
        avg_lsi = filtered['Symmetry Index'].mean()
        st.metric("Average LSI", f"{avg_lsi:.1f}%")
    else:
        unique_patients = filtered['Athlete'].nunique()
        st.metric("Unique Patients", unique_patients)
        
with col3:
    avg_pain = filtered['Pain Score'].mean()
    st.metric("Average Pain", f"{avg_pain:.1f}/10")
    
with col4:
    latest_phase = filtered.iloc[-1]['Phase'] if len(filtered) > 0 else "N/A"
    st.metric("Latest Phase", latest_phase)

# Progress visualization for individual patients
if selected_athlete != 'All Patients' and len(filtered) >= 2:
    st.subheader(f"📊 Progress Charts for {selected_athlete}")
    
    # Create progress charts
    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        # LSI Progress Chart
        fig_lsi = px.line(filtered, x='Date', y='Symmetry Index',
                         title='Limb Symmetry Index Progress',
                         markers=True)
        fig_lsi.add_hline(y=90, line_dash="dash", line_color="green",
                         annotation_text="Target LSI (90%)")
        fig_lsi.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_lsi, use_container_width=True)
    
    with fig_col2:
        # Pain Score Chart
        fig_pain = px.line(filtered, x='Date', y='Pain Score',
                          title='Pain Score Progress',
                          markers=True, color_discrete_sequence=['red'])
        fig_pain.update_layout(yaxis_range=[0, 10])
        st.plotly_chart(fig_pain, use_container_width=True)
    
    # RFD and Peak Force
    fig_col3, fig_col4 = st.columns(2)
    
    with fig_col3:
        fig_rfd = px.line(filtered, x='Date', y='RFD',
                         title='Rate of Force Development (%)',
                         markers=True, color_discrete_sequence=['purple'])
        st.plotly_chart(fig_rfd, use_container_width=True)
    
    with fig_col4:
        fig_force = px.line(filtered, x='Date', y='Peak Force',
                           title='Peak Force (N)',
                           markers=True, color_discrete_sequence=['orange'])
        st.plotly_chart(fig_force, use_container_width=True)
    
    # Progress summary
    st.subheader("📋 Progress Summary")
    
    if len(filtered) >= 2:
        first_session = filtered.iloc[0]
        latest_session = filtered.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            lsi_change = latest_session['Symmetry Index'] - first_session['Symmetry Index']
            st.metric("LSI Change", f"{lsi_change:+.1f}%", delta=f"{lsi_change:+.1f}%")
        
        with col2:
            pain_change = latest_session['Pain Score'] - first_session['Pain Score']
            st.metric("Pain Change", f"{pain_change:+.1f}", delta=f"{pain_change:+.1f}")
        
        with col3:
            rfd_change = latest_session['RFD'] - first_session['RFD']
            st.metric("RFD Change", f"{rfd_change:+.1f}%", delta=f"{rfd_change:+.1f}%")
        
        with col4:
            force_change = latest_session['Peak Force'] - first_session['Peak Force']
            st.metric("Force Change", f"{force_change:+.0f}N", delta=f"{force_change:+.0f}N")

# Overview for all patients
elif selected_athlete == 'All Patients':
    st.subheader("🔍 Patient Overview")
    
    # Patient summary table
    patient_summary = filtered.groupby('Athlete').agg({
        'Date': 'count',
        'Symmetry Index': 'mean',
        'Pain Score': 'mean',
        'RFD': 'mean',
        'Phase': 'last'
    }).round(1)
    
    patient_summary.columns = ['Sessions', 'Avg LSI', 'Avg Pain', 'Avg RFD', 'Current Phase']
    patient_summary = patient_summary.sort_values('Sessions', ascending=False)
    
    st.dataframe(patient_summary, use_container_width=True)
    
    # Population charts
    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        # LSI distribution
        fig_lsi_dist = px.histogram(filtered, x='Symmetry Index',
                                   title='LSI Distribution Across All Sessions',
                                   nbins=20)
        fig_lsi_dist.add_vline(x=90, line_dash="dash", line_color="green",
                              annotation_text="Target")
        st.plotly_chart(fig_lsi_dist, use_container_width=True)
    
    with fig_col2:
        # Phase distribution
        phase_counts = filtered['Phase'].value_counts()
        fig_phase = px.pie(values=phase_counts.values, names=phase_counts.index,
                          title='Distribution by Rehab Phase')
        st.plotly_chart(fig_phase, use_container_width=True)

# Detailed session data
st.subheader("📋 Session Details")

# Display options
display_cols = st.multiselect(
    "Select columns to display:",
    options=['Date', 'Athlete', 'Injury', 'Phase', 'Peak Force', 'Left Limb',
            'Right Limb', 'Symmetry Index', 'RFD', 'Pain Score', 'Notes'],
    default=['Date', 'Athlete', 'Phase', 'Symmetry Index', 'Pain Score', 'Notes']
)

if display_cols:
    # Format the data for display
    display_df = filtered[display_cols].copy()
    
    if 'Date' in display_cols:
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(display_df, use_container_width=True)
    
    # Export option
    if st.button("📁 Export to CSV"):
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"patient_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Alerts and recommendations
if selected_athlete != 'All Patients' and len(filtered) > 0:
    st.subheader("⚠️ Clinical Alerts")
    
    latest = filtered.iloc[-1]
    alerts = []
    
    if latest['Symmetry Index'] < 80:
        alerts.append("🔴 LSI below 80% - significant asymmetry present")
    elif latest['Symmetry Index'] < 90:
        alerts.append("🟡 LSI below 90% - monitor for re-injury risk")
    
    if latest['Pain Score'] > 5:
        alerts.append("🔴 High pain score - consider clinical review")
    elif latest['Pain Score'] > 3:
        alerts.append("🟡 Moderate pain - monitor progression")
    
    if latest['RFD'] < 70 and latest['Phase'] in ['Late', 'Return to Sport']:
        alerts.append("🟡 Low RFD for current phase - focus on explosive training")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ No clinical alerts - patient progressing well")
