import streamlit as st
import pandas as pd
import os
import re 
from datetime import datetime
from rehab_engine import get_rehab_phase, get_exercise_recommendations, get_all_exercises_for_injury_phase

# Add these video functions after your imports:
def extract_youtube_id(url):
    """Extract YouTube video ID from various YouTube URL formats"""
    if not url or not isinstance(url, str):
        return None
    
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def embed_youtube_video(video_url, width="100%", height=315):
    """Embed a YouTube video in Streamlit"""
    if not video_url or not video_url.strip():
        return False
    
    video_id = extract_youtube_id(video_url)
    if not video_id:
        return False
    
    embed_html = f"""
    <iframe 
        width="{width}" 
        height="{height}" 
        src="https://www.youtube.com/embed/{video_id}" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
    </iframe>
    """
    
    st.markdown(embed_html, unsafe_allow_html=True)
    return True

# ... rest of your existing code ...
st.title("🦿 Rehab Progression Engine")
st.markdown("""
Enter clinical or VALD-derived metrics to determine the appropriate phase of rehabilitation.
This logic is evidence-based and injury-specific, helping guide treatment decisions.
""")

# Add info about the engine
with st.expander("ℹ️ How the Rehab Engine Works"):
    st.markdown("""
    This tool uses evidence-based thresholds to determine rehabilitation phases:
    
    **Metrics Analyzed:**
    - **Limb Symmetry Index (LSI)**: Ratio between injured and uninjured limb
    - **Rate of Force Development (RFD)**: Explosive strength as % of baseline
    - **Pain Score**: Subjective pain rating (0-10 scale)
    - **Peak Force**: Maximum force output measurement
    
    **Phases:**
    - **Early**: Focus on pain management and basic movement
    - **Mid**: Progressive strengthening and functional training
    - **Late**: Advanced strengthening and sport-specific preparation
    - **Return to Sport**: Competition-ready metrics achieved
    """)

st.markdown("---")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Injury Information")
    
    # Injury selection with descriptions
    injury_options = {
        "ACL": "Anterior Cruciate Ligament",
        "Achilles": "Achilles Tendon Injury/Surgery",
        "Hamstring": "Hamstring Strain/Tear",
        "Patellar Tendon": "Patellar Tendinopathy/Rupture",
        "Rotator Cuff": "Rotator Cuff Tear/Repair",
        "Groin": "Groin/Adductor Strain",
        "Proximal Hamstring Tendinopathy": "High Hamstring Tendinopathy",
        "ATFL Ligament Injury": "Ankle Ligament Sprain"
    }
    
    injury = st.selectbox(
        "Select Injury Type",
        list(injury_options.keys()),
        format_func=lambda x: f"{x} - {injury_options[x]}"
    )
    
    # Patient information
    patient_name = st.text_input("Patient Name (Optional)", placeholder="For session logging")

with col2:
    st.subheader("📊 Clinical Metrics")
    
    # Peak force input
    peak_force = st.number_input(
        "Peak Force (N)",
        min_value=0,
        value=0,
        help="Maximum force output from testing"
    )
    
    # Limb comparison
    st.write("**Limb Comparison:**")
    limb_col1, limb_col2 = st.columns(2)
    
    with limb_col1:
        l_value = st.number_input("Left Limb (N)", min_value=0, value=0)
    with limb_col2:
        r_value = st.number_input("Right Limb (N)", min_value=0, value=0)

# Calculate LSI automatically
if max(l_value, r_value) > 0:
    asymmetry = round((min(l_value, r_value) / max(l_value, r_value)) * 100, 1)
else:
    asymmetry = 0.0

# Display LSI with color coding
if asymmetry >= 90:
    lsi_color = "normal"
elif asymmetry >= 80:
    lsi_color = "off"
else:
    lsi_color = "inverse"

st.metric(
    label="🔄 Limb Symmetry Index (LSI)",
    value=f"{asymmetry}%",
    delta=f"{asymmetry - 100:.1f}% from perfect symmetry"
)

# Additional metrics
col3, col4 = st.columns(2)

with col3:
    rfd = st.number_input(
        "Rate of Force Development (%)",
        min_value=0.0,
        max_value=200.0,
        value=0.0,
        help="RFD as percentage of baseline/uninjured limb"
    )

with col4:
    pain = st.slider(
        "Pain during test (0–10)",
        0, 10, 0,
        help="0 = No pain, 10 = Severe pain"
    )

st.markdown("---")

# Calculate button and results
if st.button("📈 Calculate Rehab Phase", use_container_width=True):
    if max(l_value, r_value) == 0:
        st.warning("⚠️ Please enter limb values to calculate LSI")
    else:
        # Get phase recommendation
        result = get_rehab_phase(injury, peak_force, asymmetry, rfd, pain)
        
        # Display results in an attractive format
        st.success(f"## 🎯 Recommended Phase: **{result['phase']}**")
        
        # Create columns for metrics display
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric("LSI", f"{asymmetry}%")
        with metric_col2:
            st.metric("RFD", f"{rfd}%")
        with metric_col3:
            st.metric("Pain", f"{pain}/10")
        
        # Show detailed message
        st.info(result['message'])
        
       # Get exercise recommendations
        recommendations = get_exercise_recommendations(injury, result['phase'])
        
        # Enhanced exercise recommendations with embedded videos
        with st.expander(f"📋 Exercise Recommendations for {result['phase']} Phase", expanded=True):
            st.markdown(f"**Focus Areas:** {', '.join(recommendations['focus'])}")
            st.markdown(f"**Recommended Exercise Types:** {', '.join(recommendations['exercise_types'])}")
            st.markdown(f"**Avoid:** {', '.join(recommendations['avoid'])}")
            
            # Show specific exercises from database
            if recommendations.get("specific_exercises"):
                st.markdown("---")
                st.subheader("🎯 Recommended Exercises")
                
                # Create tabs for exercises with videos
                exercises_with_videos = [ex for ex in recommendations["specific_exercises"] if ex.get('VideoURL') and ex['VideoURL'].strip()]
                exercises_without_videos = [ex for ex in recommendations["specific_exercises"] if not (ex.get('VideoURL') and ex['VideoURL'].strip())]
                
                if exercises_with_videos:
                    st.markdown("### 📹 Video Demonstrations")
                    
                    # Create tabs for video exercises
                    tab_names = [f"{ex['Exercise']}" for ex in exercises_with_videos]
                    tabs = st.tabs(tab_names)
                    
                    for tab, exercise in zip(tabs, exercises_with_videos):
                        with tab:
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.markdown(f"**Goal:** {exercise['Goal']}")
                                st.markdown(f"**Type:** {exercise['Type']}")
                                st.markdown(f"**Equipment:** {exercise['Equipment']}")
                                
                                if exercise['Progression'] and exercise['Progression'] != 'Not specified':
                                    st.markdown(f"**Progression:** {exercise['Progression']}")
                                
                                if exercise['Evidence'] and exercise['Evidence'] != 'Clinical experience':
                                    st.markdown(f"**Evidence:** {exercise['Evidence']}")
                            
                            with col2:
                                st.markdown("**📹 Exercise Video:**")
                                if embed_youtube_video(exercise['VideoURL'], height=250):
                                    st.success("✅ Video loaded successfully")
                                else:
                                    st.error("❌ Could not load video")
                                    st.markdown(f"[🎥 Watch on YouTube]({exercise['VideoURL']})")
                
                # Show exercises without videos
                if exercises_without_videos:
                    st.markdown("### 📝 Additional Exercises")
                    
                    for i, exercise in enumerate(exercises_without_videos):
                        with st.container():
                            st.markdown(f"**{i+1}. {exercise['Exercise']}** ({exercise['Type']})")
                            st.markdown(f"*{exercise['Goal']}*")
                            
                            if exercise['Equipment'] != 'None':
                                st.caption(f"Equipment: {exercise['Equipment']}")
                            
                            if exercise['Progression'] and exercise['Progression'] != 'Not specified':
                                with st.expander("📈 View Progression"):
                                    st.write(exercise['Progression'])
                            
                            st.markdown("---")
                
                # Button to see more exercises
                if st.button(f"🔍 Browse All {injury} Exercises"):
                    st.write(f"**All Available {injury} Exercises:**")
                    st.info("💡 Use the 'Advanced Search' page to find more exercises and filter by phase, equipment, etc.")
            
            else:
                st.info("💡 **Tip:** Add exercises with YouTube links to your database using the 'Add New Exercise' page to see video demonstrations here!")
        # Warning alerts
        if asymmetry < 90:
            st.warning("⚠️ **LSI < 90%** — Increased risk of re-injury. Consider additional strengthening.")
        if pain > 4:
            st.warning("⚠️ **High pain score** — Consider clinical reassessment and pain management.")
        if rfd < 80 and result['phase'] in ["Late", "Return to Sport"]:
            st.warning("⚠️ **Low RFD** — Focus on explosive strength and power development.")
        
        # Option to log this session
        st.markdown("---")
        st.subheader("💾 Log This Session")
        
        col_log1, col_log2 = st.columns([3, 1])
        
        with col_log1:
            session_notes = st.text_input("Session Notes (Optional)", placeholder="Additional observations or comments")
        
        with col_log2:
            if st.button("Save Session", use_container_width=True):
                try:
                    # Create session log entry
                    session_data = {
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Time": datetime.now().strftime("%H:%M"),
                        "Athlete": patient_name if patient_name else "Unknown",
                        "Injury": injury,
                        "Phase": result['phase'],
                        "Peak Force": peak_force,
                        "Left Limb": l_value,
                        "Right Limb": r_value,
                        "Symmetry Index": asymmetry,
                        "RFD": rfd,
                        "Pain Score": pain,
                        "Notes": session_notes
                    }
                    
                    # Load existing session log or create new
                    session_log_path = "session_log.csv"
                    if os.path.exists(session_log_path):
                        session_df = pd.read_csv(session_log_path)
                    else:
                        session_df = pd.DataFrame()
                    
                    # Append new session
                    new_session = pd.DataFrame([session_data])
                    session_df = pd.concat([session_df, new_session], ignore_index=True)
                    session_df.to_csv(session_log_path, index=False)
                    
                    st.success("✅ Session logged successfully!")
                    
                except Exception as e:
                    st.error(f"Error logging session: {e}")

# Show recent calculations if session log exists
try:
    session_log_path = "session_log.csv"
    if os.path.exists(session_log_path):
        session_df = pd.read_csv(session_log_path)
        if len(session_df) > 0:
            st.markdown("---")
            st.subheader("🕒 Recent Calculations")
            recent_sessions = session_df.tail(3)
            st.dataframe(
                recent_sessions[['Date', 'Athlete', 'Injury', 'Phase', 'Symmetry Index', 'Pain Score']],
                use_container_width=True
            )
except Exception:
    pass  # Ignore if file doesn't exist yet
