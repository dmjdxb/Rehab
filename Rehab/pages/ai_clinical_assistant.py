import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import math
from datetime import datetime
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="AI Clinical Assistant - Advanced Posture Analysis",
    layout="wide"
)

# Initialize MediaPipe
@st.cache_resource
def initialize_mediapipe():
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    return mp_pose, mp_drawing, mp_drawing_styles

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a = np.array(a) # First point
    b = np.array(b) # Middle point (vertex)
    c = np.array(c) # End point
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

def calculate_distance(point1, point2):
    """Calculate distance between two points"""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def analyze_posture(landmarks, image_width, image_height):
    """Comprehensive posture analysis from MediaPipe landmarks"""
    
    # Convert normalized coordinates to pixel coordinates
    def get_landmark_coords(landmark_idx):
        landmark = landmarks[landmark_idx]
        return [landmark.x * image_width, landmark.y * image_height]
    
    # Get key landmarks
    try:
        # Head and neck
        nose = get_landmark_coords(mp.solutions.pose.PoseLandmark.NOSE.value)
        left_ear = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_EAR.value)
        right_ear = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_EAR.value)
        
        # Shoulders
        left_shoulder = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value)
        right_shoulder = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value)
        
        # Hips
        left_hip = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_HIP.value)
        right_hip = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_HIP.value)
        
        # Knees
        left_knee = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_KNEE.value)
        right_knee = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value)
        
        # Ankles
        left_ankle = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value)
        right_ankle = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value)
        
    except Exception as e:
        return {"error": f"Could not extract landmarks: {str(e)}"}
    
    # Calculate posture metrics
    posture_analysis = {}
    
    # 1. Head Forward Posture Analysis
    # Calculate head position relative to shoulders
    ear_center = [(left_ear[0] + right_ear[0])/2, (left_ear[1] + right_ear[1])/2]
    shoulder_center = [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2]
    
    # Head forward distance (horizontal offset)
    head_forward_distance = abs(ear_center[0] - shoulder_center[0])
    head_forward_ratio = head_forward_distance / image_width
    
    if head_forward_ratio > 0.08:
        posture_analysis['head_forward'] = "Severe forward head posture"
        posture_analysis['head_score'] = 1
        posture_analysis['head_color'] = "🔴"
    elif head_forward_ratio > 0.05:
        posture_analysis['head_forward'] = "Moderate forward head posture"
        posture_analysis['head_score'] = 2
        posture_analysis['head_color'] = "🟠"
    elif head_forward_ratio > 0.02:
        posture_analysis['head_forward'] = "Mild forward head posture"
        posture_analysis['head_score'] = 3
        posture_analysis['head_color'] = "🟡"
    else:
        posture_analysis['head_forward'] = "Good head alignment"
        posture_analysis['head_score'] = 4
        posture_analysis['head_color'] = "🟢"
    
    # 2. Shoulder Level Analysis
    shoulder_height_diff = abs(left_shoulder[1] - right_shoulder[1])
    shoulder_diff_ratio = shoulder_height_diff / image_height
    
    if shoulder_diff_ratio > 0.04:
        posture_analysis['shoulder_level'] = "Significant shoulder asymmetry"
        posture_analysis['shoulder_score'] = 1
        posture_analysis['shoulder_color'] = "🔴"
    elif shoulder_diff_ratio > 0.02:
        posture_analysis['shoulder_level'] = "Moderate shoulder asymmetry"
        posture_analysis['shoulder_score'] = 2
        posture_analysis['shoulder_color'] = "🟠"
    elif shoulder_diff_ratio > 0.01:
        posture_analysis['shoulder_level'] = "Mild shoulder asymmetry"
        posture_analysis['shoulder_score'] = 3
        posture_analysis['shoulder_color'] = "🟡"
    else:
        posture_analysis['shoulder_level'] = "Good shoulder alignment"
        posture_analysis['shoulder_score'] = 4
        posture_analysis['shoulder_color'] = "🟢"
    
    # 3. Hip Level Analysis
    hip_height_diff = abs(left_hip[1] - right_hip[1])
    hip_diff_ratio = hip_height_diff / image_height
    
    if hip_diff_ratio > 0.03:
        posture_analysis['hip_level'] = "Significant hip asymmetry"
        posture_analysis['hip_score'] = 1
        posture_analysis['hip_color'] = "🔴"
    elif hip_diff_ratio > 0.02:
        posture_analysis['hip_level'] = "Moderate hip asymmetry"
        posture_analysis['hip_score'] = 2
        posture_analysis['hip_color'] = "🟠"
    elif hip_diff_ratio > 0.01:
        posture_analysis['hip_level'] = "Mild hip asymmetry"
        posture_analysis['hip_score'] = 3
        posture_analysis['hip_color'] = "🟡"
    else:
        posture_analysis['hip_level'] = "Good hip alignment"
        posture_analysis['hip_score'] = 4
        posture_analysis['hip_color'] = "🟢"
    
    # 4. Knee Alignment Analysis
    knee_height_diff = abs(left_knee[1] - right_knee[1])
    knee_diff_ratio = knee_height_diff / image_height
    
    if knee_diff_ratio > 0.03:
        posture_analysis['knee_level'] = "Significant knee asymmetry"
        posture_analysis['knee_score'] = 1
        posture_analysis['knee_color'] = "🔴"
    elif knee_diff_ratio > 0.02:
        posture_analysis['knee_level'] = "Moderate knee asymmetry"
        posture_analysis['knee_score'] = 2
        posture_analysis['knee_color'] = "🟠"
    elif knee_diff_ratio > 0.01:
        posture_analysis['knee_level'] = "Mild knee asymmetry"
        posture_analysis['knee_score'] = 3
        posture_analysis['knee_color'] = "🟡"
    else:
        posture_analysis['knee_level'] = "Good knee alignment"
        posture_analysis['knee_score'] = 4
        posture_analysis['knee_color'] = "🟢"
    
    # 5. Overall Body Alignment
    # Check if ear, shoulder, hip are vertically aligned (side view)
    vertical_alignment_score = 4
    
    # Calculate vertical line deviations
    shoulder_hip_offset = abs(shoulder_center[0] - (left_hip[0] + right_hip[0])/2)
    alignment_ratio = shoulder_hip_offset / image_width
    
    if alignment_ratio > 0.06:
        vertical_alignment_score = 1
        posture_analysis['alignment'] = "Poor overall alignment"
        posture_analysis['alignment_color'] = "🔴"
    elif alignment_ratio > 0.04:
        vertical_alignment_score = 2
        posture_analysis['alignment'] = "Fair overall alignment"
        posture_analysis['alignment_color'] = "🟠"
    elif alignment_ratio > 0.02:
        vertical_alignment_score = 3
        posture_analysis['alignment'] = "Good overall alignment"
        posture_analysis['alignment_color'] = "🟡"
    else:
        posture_analysis['alignment'] = "Excellent overall alignment"
        posture_analysis['alignment_color'] = "🟢"
    
    posture_analysis['alignment_score'] = vertical_alignment_score
    
    # Calculate total score
    total_score = (posture_analysis['head_score'] + 
                  posture_analysis['shoulder_score'] + 
                  posture_analysis['hip_score'] + 
                  posture_analysis['knee_score'] +
                  posture_analysis['alignment_score'])
    
    posture_analysis['total_score'] = total_score
    posture_analysis['max_score'] = 20
    posture_analysis['percentage'] = (total_score / 20) * 100
    
    # Overall assessment
    if total_score >= 18:
        posture_analysis['overall'] = "Excellent posture"
        posture_analysis['overall_color'] = "success"
        posture_analysis['risk_level'] = "Very Low"
    elif total_score >= 15:
        posture_analysis['overall'] = "Good posture"
        posture_analysis['overall_color'] = "info"
        posture_analysis['risk_level'] = "Low"
    elif total_score >= 12:
        posture_analysis['overall'] = "Fair posture - needs attention"
        posture_analysis['overall_color'] = "warning"
        posture_analysis['risk_level'] = "Moderate"
    elif total_score >= 8:
        posture_analysis['overall'] = "Poor posture - intervention needed"
        posture_analysis['overall_color'] = "error"
        posture_analysis['risk_level'] = "High"
    else:
        posture_analysis['overall'] = "Very poor posture - urgent intervention"
        posture_analysis['overall_color'] = "error"
        posture_analysis['risk_level'] = "Very High"
    
    return posture_analysis

def generate_exercise_recommendations(posture_analysis):
    """Generate specific exercise recommendations based on posture analysis"""
    recommendations = []
    
    # Head forward posture recommendations
    if posture_analysis.get('head_score', 4) < 3:
        recommendations.extend([
            "**Head & Neck:**",
            "• Chin tucks: 3 sets of 15 holds (5 seconds each)",
            "• Upper cervical strengthening exercises",
            "• Deep neck flexor strengthening",
            "• Suboccipital stretches: 3 x 30 seconds",
            "• Computer ergonomics adjustment",
            ""
        ])
    
    # Shoulder asymmetry recommendations
    if posture_analysis.get('shoulder_score', 4) < 3:
        recommendations.extend([
            "**Shoulders & Upper Back:**",
            "• Shoulder blade squeezes: 3 sets of 15",
            "• Wall slides: 2 sets of 12",
            "• Doorway chest stretches: 3 x 30 seconds each arm",
            "• Thoracic spine extension exercises",
            "• Unilateral strengthening for weaker side",
            ""
        ])
    
    # Hip asymmetry recommendations
    if posture_analysis.get('hip_score', 4) < 3:
        recommendations.extend([
            "**Hips & Pelvis:**",
            "• Hip flexor stretches: 3 x 30 seconds each side",
            "• Glute strengthening: Bridges 3 sets of 15",
            "• Clamshells: 2 sets of 12 each side",
            "• Pelvic tilts: 3 sets of 10",
            "• Single-leg stance: 3 x 30 seconds each leg",
            ""
        ])
    
    # Knee alignment recommendations
    if posture_analysis.get('knee_score', 4) < 3:
        recommendations.extend([
            "**Knee Alignment:**",
            "• Quadriceps strengthening: Straight leg raises",
            "• Hamstring stretches: 3 x 30 seconds",
            "• IT band stretches and strengthening",
            "• Balance training exercises",
            ""
        ])
    
    # Overall alignment recommendations
    if posture_analysis.get('alignment_score', 4) < 3:
        recommendations.extend([
            "**Overall Alignment:**",
            "• Core strengthening: Planks 3 x 30 seconds",
            "• Postural awareness training",
            "• Movement breaks every 30 minutes",
            "• Full-body stretching routine",
            ""
        ])
    
    # If excellent posture, maintenance recommendations
    if not recommendations:
        recommendations = [
            "**Maintenance Program:**",
            "• Continue current excellent posture habits",
            "• Regular movement breaks (every 30-60 minutes)",
            "• Maintain strength and flexibility routine",
            "• Periodic posture checks",
            "• Ergonomic workspace evaluation"
        ]
    
    return recommendations

def save_analysis_data(analysis_data, patient_name="Unknown"):
    """Save analysis data to CSV file"""
    filename = "posture_analysis_log.csv"
    
    # Prepare data for saving
    save_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patient": patient_name,
        "total_score": analysis_data.get('total_score', 0),
        "percentage": analysis_data.get('percentage', 0),
        "head_score": analysis_data.get('head_score', 0),
        "shoulder_score": analysis_data.get('shoulder_score', 0),
        "hip_score": analysis_data.get('hip_score', 0),
        "knee_score": analysis_data.get('knee_score', 0),
        "alignment_score": analysis_data.get('alignment_score', 0),
        "overall_assessment": analysis_data.get('overall', ''),
        "risk_level": analysis_data.get('risk_level', '')
    }
    
    # Create DataFrame
    df_new = pd.DataFrame([save_data])
    
    # Append to existing file or create new
    if os.path.exists(filename):
        df_existing = pd.read_csv(filename)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    
    # Save to CSV
    df_combined.to_csv(filename, index=False)
    return True

# Main App
st.title("🤖 AI Clinical Assistant - Advanced Visual Posture Analysis")
st.markdown("### *Powered by MediaPipe AI • Real-time body landmark detection*")
st.markdown("---")

# Initialize MediaPipe
try:
    mp_pose, mp_drawing, mp_drawing_styles = initialize_mediapipe()
    st.success("✅ MediaPipe AI successfully loaded!")
except Exception as e:
    st.error(f"❌ Error loading MediaPipe: {str(e)}")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.header("🎯 Analysis Settings")
    
    # Patient information
    patient_name = st.text_input("Patient Name (optional)", value="Anonymous")
    
    # Analysis mode
    analysis_mode = st.selectbox(
        "📸 Analysis Mode",
        ["Upload Image", "Take Photo", "Live Analysis (Coming Soon)"]
    )
    
    # Detection confidence
    detection_confidence = st.slider(
        "🎯 Detection Confidence",
        min_value=0.1,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Higher values = more strict detection"
    )
    
    st.markdown("---")
    st.header("📋 Instructions")
    st.markdown("""
    **For best results:**
    
    📸 **Photo Setup:**
    - Stand sideways to camera
    - Full body visible
    - Good lighting
    - Neutral standing position
    - Arms at sides
    
    👥 **Positioning:**
    - 6-8 feet from camera
    - Plain background
    - Remove bulky clothing
    - Stand naturally
    """)

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📷 Posture Analysis")
    
    if analysis_mode == "Upload Image":
        uploaded_file = st.file_uploader(
            "Choose an image for posture analysis...", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload a side-view photo showing full body"
        )
        
        if uploaded_file is not None:
            # Load and process image
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            image_height, image_width = image_array.shape[:2]
            
            # Process with MediaPipe
            with mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=detection_confidence) as pose:
                
                # Convert RGB to BGR for MediaPipe
                results = pose.process(cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
                
                # Draw landmarks on image
                annotated_image = image_array.copy()
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                
                # Display images
                st.subheader("📊 Analysis Results")
                
                # Show original and annotated images side by side
                img_col1, img_col2 = st.columns(2)
                with img_col1:
                    st.image(image, caption="Original Image", use_column_width=True)
                with img_col2:
                    st.image(annotated_image, caption="AI Analysis", use_column_width=True)
                
                # Analyze posture if landmarks detected
                if results.pose_landmarks:
                    with st.spinner("🤖 Analyzing posture..."):
                        posture_analysis = analyze_posture(
                            results.pose_landmarks.landmark, 
                            image_width, 
                            image_height
                        )
                    
                    if "error" not in posture_analysis:
                        # Display results in col2
                        with col2:
                            st.header("📊 Detailed Analysis")
                            
                            # Overall score with large display
                            score_percentage = posture_analysis['percentage']
                            st.metric(
                                "Overall Posture Score", 
                                f"{posture_analysis['total_score']}/{posture_analysis['max_score']}",
                                delta=f"{score_percentage:.1f}%"
                            )
                            
                            # Progress bar
                            st.progress(score_percentage / 100)
                            
                            # Overall status
                            if posture_analysis['overall_color'] == 'success':
                                st.success(f"✅ {posture_analysis['overall']}")
                            elif posture_analysis['overall_color'] == 'info':
                                st.info(f"ℹ️ {posture_analysis['overall']}")
                            elif posture_analysis['overall_color'] == 'warning':
                                st.warning(f"⚠️ {posture_analysis['overall']}")
                            else:
                                st.error(f"❌ {posture_analysis['overall']}")
                            
                            # Risk level
                            st.metric("Risk Level", posture_analysis['risk_level'])
                            
                            # Detailed breakdown
                            st.subheader("🔍 Detailed Breakdown")
                            
                            # Create expandable sections for each area
                            with st.expander("Head & Neck Analysis", expanded=True):
                                st.write(f"{posture_analysis['head_color']} **{posture_analysis['head_forward']}**")
                                st.write(f"Score: {posture_analysis['head_score']}/4")
                            
                            with st.expander("Shoulder Analysis"):
                                st.write(f"{posture_analysis['shoulder_color']} **{posture_analysis['shoulder_level']}**")
                                st.write(f"Score: {posture_analysis['shoulder_score']}/4")
                            
                            with st.expander("Hip Analysis"):
                                st.write(f"{posture_analysis['hip_color']} **{posture_analysis['hip_level']}**")
                                st.write(f"Score: {posture_analysis['hip_score']}/4")
                            
                            with st.expander("Knee Analysis"):
                                st.write(f"{posture_analysis['knee_color']} **{posture_analysis['knee_level']}**")
                                st.write(f"Score: {posture_analysis['knee_score']}/4")
                            
                            with st.expander("Overall Alignment"):
                                st.write(f"{posture_analysis['alignment_color']} **{posture_analysis['alignment']}**")
                                st.write(f"Score: {posture_analysis['alignment_score']}/4")
                            
                            # Save analysis button
                            if st.button("💾 Save Analysis", use_container_width=True):
                                if save_analysis_data(posture_analysis, patient_name):
                                    st.success("✅ Analysis saved successfully!")
                                else:
                                    st.error("❌ Error saving analysis")
                        
                        # Exercise recommendations below the images
                        st.subheader("💪 Personalized Exercise Recommendations")
                        recommendations = generate_exercise_recommendations(posture_analysis)
                        
                        # Display recommendations in a nice format
                        with st.container():
                            for rec in recommendations:
                                if rec.startswith("**") and rec.endswith("**"):
                                    st.markdown(f"### {rec}")
                                elif rec == "":
                                    st.markdown("")
                                else:
                                    st.markdown(rec)
                    
                    else:
                        st.error(f"❌ Analysis Error: {posture_analysis['error']}")
                
                else:
                    st.warning("⚠️ No pose detected in image. Please ensure:")
                    st.markdown("""
                    - Person is fully visible in the frame
                    - Good lighting conditions
                    - Clear background
                    - Side view positioning
                    - Try adjusting detection confidence in sidebar
                    """)
    
    elif analysis_mode == "Take Photo":
        st.info("📸 Take a side-view photo for posture analysis")
        
        # Camera input
        picture = st.camera_input("Position yourself sideways and take a photo")
        
        if picture is not None:
            # Process the captured image
            image = Image.open(picture)
            image_array = np.array(image)
            image_height, image_width = image_array.shape[:2]
            
            # Process with MediaPipe
            with mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=detection_confidence) as pose:
                
                results = pose.process(cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
                
                # Draw landmarks
                annotated_image = image_array.copy()
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
                
                # Display result
                st.image(annotated_image, caption="Your Posture Analysis", use_column_width=True)
                
                # Analyze posture if landmarks detected
                if results.pose_landmarks:
                    posture_analysis = analyze_posture(
                        results.pose_landmarks.landmark, 
                        image_width, 
                        image_height
                    )
                    
                    if "error" not in posture_analysis:
                        with col2:
                            st.header("📊 Your Results")
                            
                            # Score display
                            score_percentage = posture_analysis['percentage']
                            st.metric("Posture Score", f"{posture_analysis['total_score']}/20")
                            st.progress(score_percentage / 100)
                            
                            # Status
                            if posture_analysis['overall_color'] == 'success':
                                st.success(f"✅ {posture_analysis['overall']}")
                            elif posture_analysis['overall_color'] == 'info':
                                st.info(f"ℹ️ {posture_analysis['overall']}")
                            elif posture_analysis['overall_color'] == 'warning':
                                st.warning(f"⚠️ {posture_analysis['overall']}")
                            else:
                                st.error(f"❌ {posture_analysis['overall']}")
                            
                            st.metric("Risk Level", posture_analysis['risk_level'])
                            
                            # Save button
                            if st.button("💾 Save Analysis"):
                                if save_analysis_data(posture_analysis, patient_name):
                                    st.success("✅ Saved!")
                        
                        # Recommendations
                        st.subheader("💡 Your Exercise Plan")
                        recommendations = generate_exercise_recommendations(posture_analysis)
                        for rec in recommendations:
                            if rec.startswith("**") and rec.endswith("**"):
                                st.markdown(f"### {rec}")
                            elif rec == "":
                                st.markdown("")
                            else:
                                st.markdown(rec)
                else:
                    st.warning("⚠️ Could not detect pose. Please retake photo with better positioning.")
    
    else:  # Live Analysis
        st.info("🔴 Live camera analysis coming in future update!")
        st.markdown("""
        **Coming Soon:**
        - Real-time posture monitoring
        - Live feedback during exercises
        - Movement pattern analysis
        - Dynamic posture assessment
        """)

# Progress tracking section
if os.path.exists("posture_analysis_log.csv"):
    st.markdown("---")
    st.header("📈 Progress Tracking")
    
    try:
        df = pd.read_csv("posture_analysis_log.csv")
        if len(df) > 0:
            
            # Filter by patient if specified
            if patient_name != "Anonymous":
                patient_data = df[df['patient'] == patient_name]
                if len(patient_data) > 0:
                    st.subheader(f"Progress for {patient_name}")
                    
                    # Show recent scores
                    recent_scores = patient_data.tail(5)[['timestamp', 'total_score', 'percentage', 'overall_assessment']]
                    st.dataframe(recent_scores, use_container_width=True)
                    
                    # Progress chart
                    if len(patient_data) > 1:
                        import plotly.express as px
                        fig = px.line(patient_data, x='timestamp', y='percentage', 
                                    title=f'Posture Score Progress - {patient_name}',
                                    labels={'percentage': 'Posture Score (%)', 'timestamp': 'Date'})
                        st.plotly_chart(fig, use_container_width=True)
            
            # Overall statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Analyses", len(df))
            with col2:
                st.metric("Average Score", f"{df['percentage'].mean():.1f}%")
            with col3:
                st.metric("Latest Score", f"{df['percentage'].iloc[-1]:.1f}%")
    
    except Exception as e:
        st.error(f"Error loading progress data: {str(e)}")

# Footer
st.markdown("---")
st.caption("🤖 AI Clinical Assistant • Advanced posture analysis powered by MediaPipe • Evidence-based exercise recommendations")
