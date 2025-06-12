import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from patient_session_manager import PatientSessionManager

patient_id = PatientSessionManager.create_patient_selector()
if patient_id:
    patient = PatientSessionManager.get_current_patient()
    # Your page code with patient context

st.title("➕ Add New Exercise")
st.markdown("Fill out the details below to submit a new exercise to the shared index. All submissions are saved locally and can be reviewed before publishing.")

# Define file path (relative to app root)
csv_path = "exercise_index_master.csv"

# Load existing data or create new DataFrame
try:
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        st.success(f"✅ Loaded existing database with {len(df)} exercises")
    else:
        df = pd.DataFrame(columns=[
            "Injury", "Phase", "Exercise", "Type", "Goal",
            "Equipment", "Progression", "Evidence", "VideoURL", "DateAdded"
        ])
        st.info("📝 Creating new exercise database")
except Exception as e:
    st.error(f"Error loading database: {e}")
    df = pd.DataFrame(columns=[
        "Injury", "Phase", "Exercise", "Type", "Goal",
        "Equipment", "Progression", "Evidence", "VideoURL", "DateAdded"
    ])

# Helper function to validate YouTube URL
def is_valid_youtube_url(url):
    """Validate YouTube URL formats"""
    if not url:
        return True  # Empty URL is acceptable
    
    youtube_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'https?://(?:www\.)?youtu\.be/[\w-]+',
        r'https?://(?:m\.)?youtube\.com/watch\?v=[\w-]+',
    ]
    
    return any(re.match(pattern, url) for pattern in youtube_patterns)

# Show current database stats
if len(df) > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Exercises", len(df))
    with col2:
        st.metric("Injury Types", df['Injury'].nunique() if 'Injury' in df.columns else 0)
    with col3:
        st.metric("Most Recent", df['Exercise'].iloc[-1] if len(df) > 0 else "None")

st.markdown("---")

# Form for adding exercises
with st.form("add_exercise", clear_on_submit=True):
    st.subheader("📋 Exercise Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        injury = st.selectbox("Injury Type", [
            "ACL", "Achilles", "Hamstring", "Patellar Tendon",
            "Rotator Cuff", "Groin", "Proximal Hamstring Tendinopathy",
            "ATFL Ligament Injury", "Ankle Sprain", "Knee Meniscus",
            "Hip Labrum", "Lower Back", "Shoulder Impingement", "Other"
        ])
        
        phase = st.selectbox("Rehab Phase", [
            "Early", "Mid", "Late", "Return to Sport"
        ])
        
        ex_type = st.selectbox("Exercise Type", [
            "Strength", "Mobility", "Isometric", "Plyometric",
            "Neuromuscular", "Cardiovascular", "Balance", "Coordination"
        ])
        
    with col2:
        name = st.text_input("Exercise Name*", placeholder="e.g., Single Leg Glute Bridge")
        
        goal = st.text_input("Goal / Purpose*", placeholder="e.g., Improve hip stability and glute strength")
        
        equipment = st.text_input("Equipment Needed", placeholder="e.g., Resistance band, stability ball")
    
    # Full width fields
    progression = st.text_area("Suggested Progression",
                              placeholder="Describe how to progress this exercise (sets, reps, load, complexity)",
                              height=100)
    
    evidence = st.text_input("Evidence Source",
                           placeholder="Study author, journal, clinical guideline, or expert consensus")
    
    video_url = st.text_input("YouTube Video Link (Optional)",
                             placeholder="https://www.youtube.com/watch?v=...")
    
    # Form validation and submission
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.caption("*Required fields")
    
    with col2:
        submitted = st.form_submit_button("💾 Submit Exercise", use_container_width=True)

# Handle form submission
if submitted:
    # Validation
    errors = []
    
    if not name.strip():
        errors.append("Exercise name is required")
    if not goal.strip():
        errors.append("Goal/purpose is required")
    if video_url and not is_valid_youtube_url(video_url):
        errors.append("Please enter a valid YouTube URL")
    
    # Check for duplicate exercises
    if len(df) > 0 and name.strip().lower() in df['Exercise'].str.lower().values:
        errors.append(f"Exercise '{name}' already exists in the database")
    
    if errors:
        for error in errors:
            st.error(f"❌ {error}")
    else:
        try:
            # Create new entry
            new_entry = pd.DataFrame([{
                "Injury": injury,
                "Phase": phase,
                "Exercise": name.strip(),
                "Type": ex_type,
                "Goal": goal.strip(),
                "Equipment": equipment.strip() if equipment else "None",
                "Progression": progression.strip() if progression else "Not specified",
                "Evidence": evidence.strip() if evidence else "Clinical experience",
                "VideoURL": video_url.strip() if video_url else "",
                "DateAdded": datetime.now().strftime("%Y-%m-%d")
            }])
            
            # Append to dataframe and save
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(csv_path, index=False)
            
            st.success(f"✅ '{name}' successfully added to the exercise database!")
            st.balloons()
            
            # Show the added exercise
            st.subheader("📝 Exercise Added:")
            st.dataframe(new_entry, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error saving exercise: {e}")

# Show recent additions
if len(df) > 0:
    st.markdown("---")
    st.subheader("🕒 Recent Additions")
    
    # Show last 5 exercises added
    recent_df = df.tail(5).copy()
    if 'DateAdded' in recent_df.columns:
        recent_df = recent_df.sort_values('DateAdded', ascending=False)
    
    st.dataframe(
        recent_df[['Exercise', 'Injury', 'Phase', 'Type', 'DateAdded']],
        use_container_width=True
    )
