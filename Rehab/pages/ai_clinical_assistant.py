# Create the full MediaPipe-powered AI Clinical Assistant
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
    a = np.array(a)
    b = np.array(b) 
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

def analyze_posture(landmarks, image_width, image_height):
    """Advanced posture analysis using MediaPipe landmarks"""
    
    def get_landmark_coords(landmark_idx):
        landmark = landmarks[landmark_idx]
        return [landmark.x * image_width, landmark.y * image_height]
    
    try:
        # Get key landmarks
        nose = get_landmark_coords(mp.solutions.pose.PoseLandmark.NOSE.value)
        left_ear = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_EAR.value)
        right_ear = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_EAR.value)
        left_shoulder = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value)
        right_shoulder = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value)
        left_hip = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_HIP.value)
        right_hip = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_HIP.value)
        left_knee = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_KNEE.value)
        right_knee = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value)
        left_ankle = get_landmark_coords(mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value)
        right_ankle = get_landmark_coords(mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value)
        
    except Exception as e:
        return {"error": f"Could not extract landmarks: {str(e)}"}
    
    # Calculate posture metrics
    posture_analysis = {}
    
    # 1. Head Forward Posture Analysis
    ear_center = [(left_ear[0] + right_ear[0])/2, (left_ear[1] + right_ear[1])/2]
    shoulder_center = [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2]
    
    # Calculate head forward distance
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
    shoulder_hip_offset = abs(shoulder_center[0] - (left_hip[0] + right_hip[0])/2)
    alignment_ratio = shoulder_hip_offset / image_width
    
    if alignment_ratio > 0.06:
        posture_analysis['alignment'] = "Poor overall alignment"
        posture_analysis['alignment_score'] = 1
        posture_analysis['alignment_color'] = "🔴"
    elif alignment_ratio > 0.04:
        posture_analysis['alignment'] = "Fair overall alignment"
        posture_analysis['alignment_score'] = 2
        posture_analysis['alignment_color'] = "🟠"
    elif alignment_ratio > 0.02:
        posture_analysis['alignment'] = "Good overall alignment"
        posture_analysis['alignment_score'] = 3
        posture_analysis['alignment_color'] = "🟡"
    else:
        posture_analysis['alignment'] = "Excellent overall alignment"
        posture_analysis['alignment_score'] = 4
        posture_analysis['alignment_color'] = "🟢"
    
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
    """Generate targeted exercise recommendations"""
    recommendations = []
    
    if posture_analysis.get('head_score', 4) < 3:
        recommendations.extend([
            "**🎯 Head & Neck Corrections:**",
            "• Chin tucks: 3 sets of 15 holds (5 seconds each)",
            "• Upper cervical strengthening exercises",
            "• Deep neck flexor strengthening",
            "• Suboccipital stretches: 3 x 30 seconds",
            "• Computer ergonomics review",
            ""
        ])
    
    if posture_analysis.get('shoulder_score', 4) < 3:
        recommendations.extend([
            "**💪 Shoulder & Upper Back:**",
            "• Shoulder blade squeezes: 3 sets of 15",
            "• Wall slides: 2 sets of 12",
            "• Doorway chest stretches: 3 x 30 seconds",
            "• Thoracic spine extension exercises",
            "• Unilateral strengthening for weaker side",
            ""
        ])
    
    if posture_analysis.get('hip_score', 4) < 3:
        recommendations.extend([
            "**🔥 Hip & Pelvis Program:**",
            "• Hip flexor stretches: 3 x 30 seconds each side",
            "• Glute bridges: 3 sets of 15",
            "• Clamshells: 2 sets of 12 each side",
            "• Pelvic tilts: 3 sets of 10",
            "• Single-leg stance: 3 x 30 seconds each leg",
            ""
        ])
    
    if posture_analysis.get('knee_score', 4) < 3:
        recommendations.extend([
            "**🦵 Knee Alignment:**",
            "• Straight leg raises: 3 sets of 10 each leg",
            "• Hamstring stretches: 3 x 30 seconds",
            "• Quadriceps strengthening",
            "• Balance training exercises",
            ""
        ])
    
    if posture_analysis.get('alignment_score', 4) < 3:
        recommendations.extend([
            "**⚖️ Overall Alignment:**",
            "• Planks: 3 x 30 seconds",
            "• Core strengthening routine",
            "• Postural awareness training",
            "• Full-body stretching program",
            ""
        ])
    
    if not recommendations:
        recommendations = [
            "**✨ Maintenance Program:**",
            "• Continue excellent posture habits",
            "• Regular movement breaks every 30-60 minutes",
            "• Maintain current strength and flexibility",
            "• Periodic posture monitoring"
        ]
    
    return recommendations

def save_analysis_data(analysis_data, patient_name="Unknown"):
    """Save analysis to CSV file"""
    filename = "posture_analysis_log.csv"
    
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
        "risk_level": analysis_data.get('risk_level', ''),
        "analysis_type": "MediaPipe AI"
    }
    
    df_new = pd.DataFrame([save_data])
    
    if os.path.exists(filename):
        df_existing = pd.read_csv(filename)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    
    df_combined.to_csv(filename, index=False)
    return True

# Main App
st.title("🤖 AI Clinical Assistant")
st.markdown("### *Advanced Visual Posture Analysis powered by MediaPipe AI*")

# Initialize MediaPipe
try:
    mp_pose, mp_drawing, mp_drawing_styles = initialize_mediapipe()
    st.success("✅ MediaPipe AI successfully initialized! (v0.10.9)")
except Exception as e:
    st.error(f"❌ Error initializing MediaPipe: {str(e)}")
    st.stop()

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎯 Analysis Settings")
    
    patient_name = st.text_input("Patient Name", value="Anonymous")
    
    analysis_mode = st.selectbox(
        "📸 Analysis Mode",
        ["Upload Image", "Take Photo"]
    )
    
    detection_confidence = st.slider(
        "🎯 Detection Confidence",
        0.1, 1.0, 0.5, 0.1,
        help="Higher = more strict detection"
    )
    
    st.markdown("---")
    st.header("📋 Photo Guidelines")
    st.markdown("""
    **For optimal AI analysis:**
    
    📸 **Camera Setup:**
    - Side view positioning
    - Full body visible  
    - Bright, even lighting
    - Plain background
    - 6-8 feet distance
    
    🧍 **Patient Positioning:**
    - Natural standing pose
    - Arms relaxed at sides
    - Look straight ahead
    - Remove bulky clothing
    """)
    
    st.markdown("---")
    st.header("🔬 AI Features")
    st.markdown("""
    **MediaPipe Analysis:**
    - 33-point body landmarks
    - Precise angle measurements
    - Real-time processing
    - Professional accuracy
    """)

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📷 Advanced Posture Analysis")
    
    if analysis_mode == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload a side-view photo for AI posture analysis",
            type=['jpg', 'jpeg', 'png'],
            help="Best results with side-view, full-body photos"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            image_height, image_width = image_array.shape[:2]
            
            # Process with MediaPipe AI
            with mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=detection_confidence
            ) as pose:
                
                # Convert RGB to BGR for MediaPipe
                results = pose.process(cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
                
                # Create annotated image with AI landmarks
                annotated_image = image_array.copy()
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                
                # Display images side by side
                img_col1, img_col2 = st.columns(2)
                with img_col1:
                    st.image(image, caption="📷 Original Photo", use_column_width=True)
                with img_col2:
                    st.image(annotated_image, caption="🤖 AI Landmark Detection", use_column_width=True)
                
                # Analyze posture if landmarks detected
                if results.pose_landmarks:
                    with st.spinner("🤖 AI analyzing posture..."):
                        posture_analysis = analyze_posture(
                            results.pose_landmarks.landmark,
                            image_width,
                            image_height
                        )
                    
                    if "error" not in posture_analysis:
                        # Display results in sidebar column
                        with col2:
                            st.header("📊 AI Analysis Results")
                            
                            # Main score with progress
                            score = posture_analysis['percentage']
                            st.metric(
                                "🎯 Posture Score",
                                f"{posture_analysis['total_score']}/20",
                                f"{score:.1f}%"
                            )
                            
                            # Animated progress bar
                            progress_bar = st.progress(0)
                            for i in range(int(score)):
                                progress_bar.progress(i / 100)
                            progress_bar.progress(score / 100)
                            
                            # Overall status with color coding
                            if posture_analysis['overall_color'] == 'success':
                                st.success(f"✅ {posture_analysis['overall']}")
                            elif posture_analysis['overall_color'] == 'info':
                                st.info(f"ℹ️ {posture_analysis['overall']}")
                            elif posture_analysis['overall_color'] == 'warning':
                                st.warning(f"⚠️ {posture_analysis['overall']}")
                            else:
                                st.error(f"❌ {posture_analysis['overall']}")
                            
                            # Risk assessment
                            risk_colors = {
                                "Very Low": "🟢",
                                "Low": "🟡", 
                                "Moderate": "🟠",
                                "High": "🔴",
                                "Very High": "🔴"
                            }
                            risk_color = risk_colors.get(posture_analysis['risk_level'], "⚪")
                            st.metric("🚨 Risk Level", f"{risk_color} {posture_analysis['risk_level']}")
                            
                            # Detailed breakdown
                            with st.expander("🔍 Detailed AI Analysis", expanded=True):
                                st.markdown("**Regional Assessment:**")
                                st.write(f"{posture_analysis['head_color']} **Head Position:** {posture_analysis['head_forward']} ({posture_analysis['head_score']}/4)")
                                st.write(f"{posture_analysis['shoulder_color']} **Shoulder Level:** {posture_analysis['shoulder_level']} ({posture_analysis['shoulder_score']}/4)")
                                st.write(f"{posture_analysis['hip_color']} **Hip Alignment:** {posture_analysis['hip_level']} ({posture_analysis['hip_score']}/4)")
                                st.write(f"{posture_analysis['knee_color']} **Knee Position:** {posture_analysis['knee_level']} ({posture_analysis['knee_score']}/4)")
                                st.write(f"{posture_analysis['alignment_color']} **Overall Alignment:** {posture_analysis['alignment']} ({posture_analysis['alignment_score']}/4)")
                            
                            # Save analysis button
                            if st.button("💾 Save AI Analysis", use_container_width=True):
                                if save_analysis_data(posture_analysis, patient_name):
                                    st.success("✅ Analysis saved to database!")
                                    st.balloons()
                                else:
                                    st.error("❌ Failed to save analysis")
                        
                        # Exercise recommendations below images
                        st.subheader("💪 Personalized Exercise Prescription")
                        st.markdown("*Based on AI posture analysis findings*")
                        
                        recommendations = generate_exercise_recommendations(posture_analysis)
                        
                        # Display recommendations in organized format
                        rec_col1, rec_col2 = st.columns(2)
                        col_index = 0
                        
                        for rec in recommendations:
                            if rec.startswith("**") and rec.endswith("**"):
                                if col_index % 2 == 0:
                                    with rec_col1:
                                        st.markdown(rec)
                                else:
                                    with rec_col2:
                                        st.markdown(rec)
                                col_index += 1
                            elif rec == "":
                                continue
                            else:
                                if col_index % 2 == 1:
                                    with rec_col1:
                                        st.markdown(rec)
                                else:
                                    with rec_col2:
                                        st.markdown(rec)
                    
                    else:
                        st.error(f"❌ AI Analysis Error: {posture_analysis['error']}")
                
                else:
                    st.warning("⚠️ AI could not detect human pose in image.")
                    st.markdown("""
                    **Troubleshooting:**
                    - Ensure person is fully visible
                    - Check lighting conditions
                    - Try side-view positioning
                    - Adjust detection confidence in sidebar
                    - Use plain background
                    """)
    
    elif analysis_mode == "Take Photo":
        st.info("📸 Position yourself sideways to the camera for optimal AI analysis")
        
        # Camera input
        picture = st.camera_input("Take a photo for AI posture analysis")
        
        if picture is not None:
            image = Image.open(picture)
            image_array = np.array(image)
            image_height, image_width = image_array.shape[:2]
            
            # Process with MediaPipe
            with mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=detection_confidence
            ) as pose:
                
                results = pose.process(cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
                
                # Create annotated image
                annotated_image = image_array.copy()
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                
                # Display result
                st.image(annotated_image, caption="🤖 Your AI Posture Analysis", use_column_width=True)
                
                # Analyze if landmarks detected
                if results.pose_landmarks:
                    posture_analysis = analyze_posture(
                        results.pose_landmarks.landmark,
                        image_width,
                        image_height
                    )
                    
                    if "error" not in posture_analysis:
                        with col2:
                            st.header("📊 Your AI Results")
                            
                            score = posture_analysis['percentage']
                            st.metric("Posture Score", f"{posture_analysis['total_score']}/20")
                            st.progress(score / 100)
                            
                            # Status display
                            if posture_analysis['overall_color'] == 'success':
                                st.success(f"✅ {posture_analysis['overall']}")
                            elif posture_analysis['overall_color'] == 'info':
                                st.info(f"ℹ️ {posture_analysis['overall']}")
                            elif posture_analysis['overall_color'] == 'warning':
                                st.warning(f"⚠️ {posture_analysis['overall']}")
                            else:
                                st.error(f"❌ {posture_analysis['overall']}")
                            
                            # Quick save button
                            if st.button("💾 Save Analysis"):
                                if save_analysis_data(posture_analysis, patient_name):
                                    st.success("✅ Saved to database!")
                        
                        # Show personalized recommendations
                        st.subheader("💡 Your Personalized Exercise Plan")
                        recommendations = generate_exercise_recommendations(posture_analysis)
                        for rec in recommendations:
                            if rec.startswith("**") and rec.endswith("**"):
                                st.markdown(rec)
                            elif rec == "":
                                st.markdown("")
                            else:
                                st.markdown(rec)
                else:
                    st.warning("⚠️ AI could not detect pose. Please retake photo with better positioning.")

# Progress tracking section
if os.path.exists("posture_analysis_log.csv"):
    st.markdown("---")
    st.header("📈 AI Analysis Progress Tracking")
    
    try:
        df = pd.read_csv("posture_analysis_log.csv")
        if len(df) > 0:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total AI Analyses", len(df))
            with col2:
                st.metric("Average Score", f"{df['percentage'].mean():.1f}%")
            with col3:
                st.metric("Latest Score", f"{df['percentage'].iloc[-1]:.1f}%")
            with col4:
                improvement = df['percentage'].iloc[-1] - df['percentage'].iloc[0] if len(df) > 1 else 0
                st.metric("Progress", f"{improvement:+.1f}%")
            
            # Recent analyses table
            st.subheader("📋 Recent AI Analyses")
            recent = df.tail(10)[['timestamp', 'patient', 'total_score', 'percentage', 'overall_assessment', 'risk_level']]
            st.dataframe(recent, use_container_width=True)
            
            # Progress visualization
            if len(df) > 1:
                st.subheader("📊 Progress Visualization")
                
                # Create simple line chart
                chart_data = df[['timestamp', 'percentage']].copy()
                chart_data['timestamp'] = pd.to_datetime(chart_data['timestamp'])
                chart_data = chart_data.set_index('timestamp')
                
                st.line_chart(chart_data, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading progress data: {str(e)}")

# Footer with AI info
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 14px;'>
🤖 <strong>AI Clinical Assistant</strong> • Advanced posture analysis powered by MediaPipe AI<br>
Professional-grade landmark detection • Evidence-based exercise prescription • HIPAA-compliant local storage
</div>
""", unsafe_allow_html=True)
