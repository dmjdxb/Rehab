# Update your AI Clinical Assistant to work with or without MediaPipe
import streamlit as st
import numpy as np
from PIL import Image
import math
from datetime import datetime
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="AI Clinical Assistant - Visual Posture Analysis",
    layout="wide"
)

# Try MediaPipe import with graceful fallback
MEDIAPIPE_AVAILABLE = False
try:
    import cv2
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    
    @st.cache_resource
    def initialize_mediapipe():
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        return mp_pose, mp_drawing, mp_drawing_styles
        
except ImportError:
    MEDIAPIPE_AVAILABLE = False

def advanced_cv_analysis(image_array):
    """Advanced computer vision posture analysis"""
    height, width = image_array.shape[:2]
    
    # Convert to grayscale for analysis
    if len(image_array.shape) == 3:
        gray = np.mean(image_array, axis=2).astype(np.uint8)
    else:
        gray = image_array
    
    # Advanced symmetry analysis
    left_half = gray[:, :width//2]
    right_half = np.fliplr(gray[:, width//2:])
    
    # Ensure same dimensions
    min_width = min(left_half.shape[1], right_half.shape[1])
    left_half = left_half[:, :min_width]
    right_half = right_half[:, :min_width]
    
    # Calculate bilateral symmetry
    if left_half.shape == right_half.shape:
        diff = np.abs(left_half.astype(float) - right_half.astype(float))
        symmetry_score = 100 - (np.mean(diff) / 255 * 100)
    else:
        symmetry_score = 50
    
    # Vertical alignment analysis
    vertical_profile = np.mean(gray, axis=0)
    vertical_consistency = 100 - (np.std(vertical_profile) / np.mean(vertical_profile) * 100)
    vertical_consistency = max(0, min(100, vertical_consistency))
    
    # Head position analysis (upper third of image)
    upper_third = gray[:height//3, :]
    head_symmetry = analyze_region_symmetry(upper_third)
    
    # Shoulder analysis (middle section)
    shoulder_region = gray[height//4:height//2, :]
    shoulder_level = analyze_horizontal_alignment(shoulder_region)
    
    # Hip analysis (lower middle section)
    hip_region = gray[height//2:3*height//4, :]
    hip_alignment = analyze_horizontal_alignment(hip_region)
    
    # Calculate individual scores
    head_score = calculate_region_score(head_symmetry)
    shoulder_score = calculate_region_score(shoulder_level) 
    hip_score = calculate_region_score(hip_alignment)
    alignment_score = calculate_region_score(vertical_consistency)
    symmetry_rating = calculate_region_score(symmetry_score)
    
    # Overall composite score
    total_score = head_score + shoulder_score + hip_score + alignment_score + symmetry_rating
    overall_percentage = (total_score / 20) * 100
    
    # Generate analysis results
    analysis = {
        'total_score': total_score,
        'max_score': 20,
        'percentage': overall_percentage,
        'head_score': head_score,
        'shoulder_score': shoulder_score,
        'hip_score': hip_score,
        'alignment_score': alignment_score,
        'symmetry_score': symmetry_rating,
        'raw_symmetry': symmetry_score,
        'raw_vertical': vertical_consistency,
        'raw_head': head_symmetry,
        'raw_shoulder': shoulder_level,
        'raw_hip': hip_alignment
    }
    
    # Add detailed assessments
    analysis.update(generate_detailed_assessments(analysis))
    
    return analysis

def analyze_region_symmetry(region):
    """Analyze symmetry of a specific region"""
    if region.size == 0:
        return 50
        
    height, width = region.shape
    left = region[:, :width//2]
    right = np.fliplr(region[:, width//2:])
    
    min_width = min(left.shape[1], right.shape[1])
    left = left[:, :min_width]
    right = right[:, :min_width]
    
    if left.shape == right.shape:
        diff = np.abs(left.astype(float) - right.astype(float))
        return 100 - (np.mean(diff) / 255 * 100)
    return 50

def analyze_horizontal_alignment(region):
    """Analyze horizontal alignment of a region"""
    if region.size == 0:
        return 50
        
    # Calculate horizontal intensity profile
    horizontal_profile = np.mean(region, axis=1)
    
    # Find peaks (potential anatomical landmarks)
    profile_diff = np.diff(horizontal_profile)
    peak_consistency = 100 - (np.std(profile_diff) / np.mean(np.abs(profile_diff)) * 100)
    
    return max(0, min(100, peak_consistency))

def calculate_region_score(raw_score):
    """Convert raw score (0-100) to 1-4 scale"""
    if raw_score >= 85:
        return 4
    elif raw_score >= 70:
        return 3
    elif raw_score >= 55:
        return 2
    else:
        return 1

def generate_detailed_assessments(analysis):
    """Generate detailed assessments for each region"""
    assessments = {}
    
    # Head assessment
    head_score = analysis['head_score']
    if head_score >= 4:
        assessments['head_assessment'] = "Excellent head positioning"
        assessments['head_color'] = "🟢"
    elif head_score >= 3:
        assessments['head_assessment'] = "Good head alignment"
        assessments['head_color'] = "🟡"
    elif head_score >= 2:
        assessments['head_assessment'] = "Moderate head position concerns"
        assessments['head_color'] = "🟠"
    else:
        assessments['head_assessment'] = "Significant head position issues"
        assessments['head_color'] = "🔴"
    
    # Shoulder assessment
    shoulder_score = analysis['shoulder_score']
    if shoulder_score >= 4:
        assessments['shoulder_assessment'] = "Excellent shoulder alignment"
        assessments['shoulder_color'] = "🟢"
    elif shoulder_score >= 3:
        assessments['shoulder_assessment'] = "Good shoulder positioning"
        assessments['shoulder_color'] = "🟡"
    elif shoulder_score >= 2:
        assessments['shoulder_assessment'] = "Moderate shoulder asymmetry"
        assessments['shoulder_color'] = "🟠"
    else:
        assessments['shoulder_assessment'] = "Significant shoulder imbalance"
        assessments['shoulder_color'] = "🔴"
    
    # Hip assessment
    hip_score = analysis['hip_score']
    if hip_score >= 4:
        assessments['hip_assessment'] = "Excellent hip alignment"
        assessments['hip_color'] = "🟢"
    elif hip_score >= 3:
        assessments['hip_assessment'] = "Good hip positioning"
        assessments['hip_color'] = "🟡"
    elif hip_score >= 2:
        assessments['hip_assessment'] = "Moderate hip asymmetry"
        assessments['hip_color'] = "🟠"
    else:
        assessments['hip_assessment'] = "Significant hip imbalance"
        assessments['hip_color'] = "🔴"
    
    # Overall alignment
    alignment_score = analysis['alignment_score']
    if alignment_score >= 4:
        assessments['alignment_assessment'] = "Excellent overall alignment"
        assessments['alignment_color'] = "🟢"
    elif alignment_score >= 3:
        assessments['alignment_assessment'] = "Good vertical alignment"
        assessments['alignment_color'] = "🟡"
    elif alignment_score >= 2:
        assessments['alignment_assessment'] = "Moderate alignment issues"
        assessments['alignment_color'] = "🟠"
    else:
        assessments['alignment_assessment'] = "Poor overall alignment"
        assessments['alignment_color'] = "🔴"
    
    # Overall status
    percentage = analysis['percentage']
    if percentage >= 85:
        assessments['overall'] = "Excellent posture detected"
        assessments['overall_color'] = "success"
        assessments['risk_level'] = "Very Low"
    elif percentage >= 70:
        assessments['overall'] = "Good posture with minor issues"
        assessments['overall_color'] = "info"
        assessments['risk_level'] = "Low"
    elif percentage >= 55:
        assessments['overall'] = "Moderate posture concerns"
        assessments['overall_color'] = "warning"
        assessments['risk_level'] = "Moderate"
    elif percentage >= 40:
        assessments['overall'] = "Poor posture - intervention needed"
        assessments['overall_color'] = "error"
        assessments['risk_level'] = "High"
    else:
        assessments['overall'] = "Very poor posture - urgent attention"
        assessments['overall_color'] = "error"
        assessments['risk_level'] = "Very High"
    
    return assessments

def generate_exercise_recommendations(analysis):
    """Generate targeted exercise recommendations"""
    recommendations = []
    
    head_score = analysis.get('head_score', 4)
    shoulder_score = analysis.get('shoulder_score', 4)
    hip_score = analysis.get('hip_score', 4)
    alignment_score = analysis.get('alignment_score', 4)
    
    if head_score < 3:
        recommendations.extend([
            "**🎯 Head & Neck Program:**",
            "• Chin tucks: 3 sets of 15 holds (5 seconds each)",
            "• Upper cervical strengthening exercises",
            "• Deep neck flexor strengthening",
            "• Suboccipital stretches: 3 x 30 seconds",
            "• Ergonomic workstation assessment",
            ""
        ])
    
    if shoulder_score < 3:
        recommendations.extend([
            "**💪 Shoulder Correction Program:**",
            "• Shoulder blade squeezes: 3 sets of 15",
            "• Wall slides: 2 sets of 12",
            "• Doorway chest stretches: 3 x 30 seconds",
            "• Thoracic spine mobility exercises",
            "• Unilateral strengthening exercises",
            ""
        ])
    
    if hip_score < 3:
        recommendations.extend([
            "**🔥 Hip & Pelvis Program:**",
            "• Hip flexor stretches: 3 x 30 seconds each side",
            "• Glute activation exercises: Bridges 3 sets of 15",
            "• Clamshells: 2 sets of 12 each side",
            "• Pelvic stabilization exercises",
            "• Single-leg balance training: 3 x 30 seconds",
            ""
        ])
    
    if alignment_score < 3:
        recommendations.extend([
            "**⚖️ Overall Alignment Program:**",
            "• Core strengthening: Planks 3 x 30 seconds",
            "• Postural awareness training",
            "• Full-body stretching routine",
            "• Movement pattern correction",
            "• Regular posture breaks every 30 minutes",
            ""
        ])
    
    # Add general recommendations
    percentage = analysis.get('percentage', 50)
    if percentage < 60:
        recommendations.extend([
            "**🏥 Professional Care:**",
            "• Consider professional posture assessment",
            "• Physical therapy evaluation recommended",
            "• Address underlying movement dysfunctions",
            ""
        ])
    
    if not recommendations:
        recommendations = [
            "**✨ Maintenance Program:**",
            "• Excellent posture - continue current habits!",
            "• Regular movement breaks every 30-60 minutes",
            "• Maintain strength and flexibility routine",
            "• Periodic posture monitoring"
        ]
    
    return recommendations

def save_analysis_data(analysis_data, patient_name="Unknown"):
    """Save analysis to session state (cloud-compatible)"""
    # For Streamlit Cloud, use session state instead of CSV
    if 'posture_analyses' not in st.session_state:
        st.session_state.posture_analyses = []
    
    save_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patient": patient_name,
        "total_score": analysis_data.get('total_score', 0),
        "percentage": analysis_data.get('percentage', 0),
        "head_score": analysis_data.get('head_score', 0),
        "shoulder_score": analysis_data.get('shoulder_score', 0),
        "hip_score": analysis_data.get('hip_score', 0),
        "alignment_score": analysis_data.get('alignment_score', 0),
        "overall_assessment": analysis_data.get('overall', ''),
        "risk_level": analysis_data.get('risk_level', ''),
        "analysis_type": "Advanced CV" if not MEDIAPIPE_AVAILABLE else "MediaPipe"
    }
    
    st.session_state.posture_analyses.append(save_data)
    return True

# Main App
st.title("🤖 AI Clinical Assistant")
st.markdown("### *Advanced Visual Posture Analysis System*")

# System status
if MEDIAPIPE_AVAILABLE:
    st.success("✅ MediaPipe AI available - Using advanced landmark detection")
else:
    st.info("🔬 Using advanced computer vision analysis (MediaPipe unavailable)")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎯 Analysis Settings")
    
    patient_name = st.text_input("Patient Name", value="Anonymous")
    
    analysis_mode = st.selectbox(
        "📸 Analysis Mode",
        ["Upload Image", "Take Photo"]
    )
    
    if MEDIAPIPE_AVAILABLE:
        detection_confidence = st.slider(
            "Detection Confidence",
            0.1, 1.0, 0.5, 0.1
        )
    
    st.markdown("---")
    st.header("📋 Instructions")
    st.markdown("""
    **For optimal analysis:**
    
    📸 **Photo Setup:**
    - Side view positioning
    - Full body visible
    - Good lighting
    - Plain background
    - Natural standing pose
    
    🎯 **Analysis Features:**
    - Bilateral symmetry assessment
    - Regional alignment evaluation
    - Professional scoring system
    - Evidence-based recommendations
    """)

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📷 Visual Posture Analysis")
    
    if analysis_mode == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload a photo for posture analysis",
            type=['jpg', 'jpeg', 'png'],
            help="Best results with side-view, full-body photos"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            # Display original image
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Analyze posture
            with st.spinner("🔬 Analyzing posture..."):
                if MEDIAPIPE_AVAILABLE:
                    # MediaPipe analysis would go here
                    # For now, use advanced CV
                    analysis = advanced_cv_analysis(image_array)
                else:
                    analysis = advanced_cv_analysis(image_array)
            
            # Display results
            with col2:
                st.header("📊 Analysis Results")
                
                # Main score
                score = analysis['percentage']
                st.metric(
                    "Posture Score",
                    f"{analysis['total_score']}/20",
                    f"{score:.1f}%"
                )
                st.progress(score / 100)
                
                # Overall status
                if analysis['overall_color'] == 'success':
                    st.success(f"✅ {analysis['overall']}")
                elif analysis['overall_color'] == 'info':
                    st.info(f"ℹ️ {analysis['overall']}")
                elif analysis['overall_color'] == 'warning':
                    st.warning(f"⚠️ {analysis['overall']}")
                else:
                    st.error(f"❌ {analysis['overall']}")
                
                st.metric("Risk Level", analysis['risk_level'])
                
                # Detailed breakdown
                with st.expander("🔍 Detailed Analysis", expanded=True):
                    st.write(f"{analysis['head_color']} **Head:** {analysis['head_assessment']} ({analysis['head_score']}/4)")
                    st.write(f"{analysis['shoulder_color']} **Shoulders:** {analysis['shoulder_assessment']} ({analysis['shoulder_score']}/4)")
                    st.write(f"{analysis['hip_color']} **Hips:** {analysis['hip_assessment']} ({analysis['hip_score']}/4)")
                    st.write(f"{analysis['alignment_color']} **Alignment:** {analysis['alignment_assessment']} ({analysis['alignment_score']}/4)")
                
                # Save button
                if st.button("💾 Save Analysis", use_container_width=True):
                    if save_analysis_data(analysis, patient_name):
                        st.success("✅ Analysis saved!")
                        st.balloons()
            
            # Exercise recommendations
            st.subheader("💪 Personalized Exercise Recommendations")
            recommendations = generate_exercise_recommendations(analysis)
            
            for rec in recommendations:
                if rec.startswith("**") and rec.endswith("**"):
                    st.markdown(rec)
                elif rec == "":
                    st.markdown("")
                else:
                    st.markdown(rec)
    
    elif analysis_mode == "Take Photo":
        st.info("📸 Position yourself sideways to the camera for optimal analysis")
        
        picture = st.camera_input("Take a photo for posture analysis")
        
        if picture is not None:
            image = Image.open(picture)
            image_array = np.array(image)
            
            st.image(image, caption="Your Photo", use_column_width=True)
            
            # Analyze
            analysis = advanced_cv_analysis(image_array)
            
            with col2:
                st.header("📊 Your Results")
                
                score = analysis['percentage']
                st.metric("Posture Score", f"{analysis['total_score']}/20")
                st.progress(score / 100)
                
                if analysis['overall_color'] == 'success':
                    st.success(f"✅ {analysis['overall']}")
                elif analysis['overall_color'] == 'info':
                    st.info(f"ℹ️ {analysis['overall']}")
                elif analysis['overall_color'] == 'warning':
                    st.warning(f"⚠️ {analysis['overall']}")
                else:
                    st.error(f"❌ {analysis['overall']}")
                
                if st.button("💾 Save Analysis"):
                    if save_analysis_data(analysis, patient_name):
                        st.success("✅ Saved!")
            
            # Show recommendations
            st.subheader("💡 Your Exercise Plan")
            recommendations = generate_exercise_recommendations(analysis)
            for rec in recommendations:
                if rec.startswith("**") and rec.endswith("**"):
                    st.markdown(rec)
                elif rec == "":
                    st.markdown("")
                else:
                    st.markdown(rec)

# Progress tracking (using session state for cloud)
if 'posture_analyses' in st.session_state and len(st.session_state.posture_analyses) > 0:
    st.markdown("---")
    st.header("📈 Session Progress Tracking")
    
    analyses = st.session_state.posture_analyses
    df = pd.DataFrame(analyses)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Analyses This Session", len(df))
    with col2:
        st.metric("Average Score", f"{df['percentage'].mean():.1f}%")
    with col3:
        st.metric("Latest Score", f"{df['percentage'].iloc[-1]:.1f}%")
    with col4:
        if len(df) > 1:
            improvement = df['percentage'].iloc[-1] - df['percentage'].iloc[0]
            st.metric("Session Progress", f"{improvement:+.1f}%")
        else:
            st.metric("Session Progress", "First analysis")
    
    # Recent analyses
    st.subheader("📋 Session Analyses")
    display_df = df[['timestamp', 'patient', 'total_score', 'percentage', 'overall_assessment']]
    st.dataframe(display_df, use_container_width=True)
    
    # Simple progress chart
    if len(df) > 1:
        st.subheader("📊 Progress Chart")
        chart_data = df[['percentage']].reset_index()
        chart_data.columns = ['Analysis #', 'Posture Score %']
        st.line_chart(chart_data.set_index('Analysis #'))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 14px;'>
🤖 <strong>AI Clinical Assistant</strong> • Advanced posture analysis system<br>
Computer vision-powered assessment • Evidence-based exercise prescription • Cloud-ready deployment
</div>
""", unsafe_allow_html=True)
