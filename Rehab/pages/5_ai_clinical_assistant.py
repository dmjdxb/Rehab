import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import math
from datetime import datetime
import pandas as pd
import base64
import io

# Page configuration
st.set_page_config(
    page_title="AI Clinical Assistant - Visual Posture Analysis",
    layout="wide"
)

# Initialize session state
if 'posture_analyses' not in st.session_state:
    st.session_state.posture_analyses = []
if 'manual_landmarks' not in st.session_state:
    st.session_state.manual_landmarks = None
if 'landmarks_placed' not in st.session_state:
    st.session_state.landmarks_placed = False
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'annotated_image' not in st.session_state:
    st.session_state.annotated_image = None
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = None

def detect_body_region(image_array):
    """Detect the actual body region, excluding shadows and background"""
    height, width = image_array.shape[:2]
    
    if len(image_array.shape) == 3:
        # RGB analysis
        r, g, b = image_array[:,:,0], image_array[:,:,1], image_array[:,:,2]
        
        # Skin tone detection
        skin_mask = ((r > 95) & (g > 40) & (b > 20) & 
                     (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b) > 15) &
                     (np.abs(r - g) > 15) & (r > g) & (r > b))
        
        # Clothing detection
        gray = np.mean(image_array, axis=2)
        clothing_mask = ((gray > 30) & (gray < 200) & ~skin_mask)
        
        # Combine skin and clothing
        body_mask = skin_mask | clothing_mask
        
        # Simple noise reduction
        kernel = np.ones((3,3), np.uint8)
        body_mask = binary_erosion(body_mask, kernel)
        body_mask = binary_dilation(body_mask, kernel)
    else:
        gray = image_array
        body_mask = (gray > 50) & (gray < 220)
    
    return body_mask

def binary_erosion(image, kernel):
    """Simple binary erosion"""
    result = np.zeros_like(image, dtype=bool)
    kh, kw = kernel.shape
    padded = np.pad(image, ((kh//2, kh//2), (kw//2, kw//2)), mode='constant')
    
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded[i:i+kh, j:j+kw]
            if np.all(region[kernel == 1]):
                result[i, j] = True
    return result

def binary_dilation(image, kernel):
    """Simple binary dilation"""
    result = np.zeros_like(image, dtype=bool)
    kh, kw = kernel.shape
    padded = np.pad(image, ((kh//2, kh//2), (kw//2, kw//2)), mode='constant')
    
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded[i:i+kh, j:j+kw]
            if np.any(region[kernel == 1]):
                result[i, j] = True
    return result

def find_body_centerline(body_mask, height):
    """Find the centerline of the body at each height level"""
    centerline = []
    
    for y in range(height):
        row = body_mask[y, :]
        body_pixels = np.where(row)[0]
        
        if len(body_pixels) > 0:
            center_x = int(np.mean(body_pixels))
        else:
            center_x = centerline[-1] if centerline else body_mask.shape[1] // 2
        
        centerline.append(center_x)
    
    # Smooth the centerline
    window_size = 5
    smoothed = []
    for i in range(len(centerline)):
        start_idx = max(0, i - window_size//2)
        end_idx = min(len(centerline), i + window_size//2 + 1)
        window_values = centerline[start_idx:end_idx]
        smoothed.append(int(np.mean(window_values)))
    
    return smoothed

def find_body_boundaries(body_mask):
    """Find the top, bottom, left, and right boundaries of the body"""
    body_pixels = np.where(body_mask)
    
    if len(body_pixels[0]) > 0:
        body_top = np.min(body_pixels[0])
        body_bottom = np.max(body_pixels[0])
        body_left = np.min(body_pixels[1])
        body_right = np.max(body_pixels[1])
        return body_top, body_bottom, body_left, body_right
    else:
        return None, None, None, None

def estimate_width_at_height(body_mask, y):
    """Estimate body width at given height"""
    if y >= body_mask.shape[0]:
        return body_mask.shape[1] // 4
    
    row = body_mask[y, :]
    body_pixels = np.where(row)[0]
    
    if len(body_pixels) > 0:
        return int(np.max(body_pixels) - np.min(body_pixels))
    else:
        return body_mask.shape[1] // 4

def estimate_anatomical_landmarks(image_array):
    """Estimate key anatomical landmarks using body detection"""
    height, width = image_array.shape[:2]
    
    # Find body region
    body_mask = detect_body_region(image_array)
    body_center_x = find_body_centerline(body_mask, height)
    
    landmarks = {}
    
    # Find body boundaries
    body_top, body_bottom, body_left, body_right = find_body_boundaries(body_mask)
    
    if body_top is not None and body_bottom is not None:
        body_height = body_bottom - body_top
        
        # Head/Skull
        head_y = body_top + int(body_height * 0.12)
        head_x = body_center_x[min(head_y, len(body_center_x)-1)]
        landmarks['skull'] = (head_x, head_y)
        
        # Shoulders
        shoulder_y = body_top + int(body_height * 0.20)
        shoulder_center_x = body_center_x[min(shoulder_y, len(body_center_x)-1)]
        shoulder_width = estimate_width_at_height(body_mask, shoulder_y)
        landmarks['left_shoulder'] = (shoulder_center_x - shoulder_width//2, shoulder_y)
        landmarks['right_shoulder'] = (shoulder_center_x + shoulder_width//2, shoulder_y)
        landmarks['shoulder_center'] = (shoulder_center_x, shoulder_y)
        
        # Hips
        hip_y = body_top + int(body_height * 0.55)
        hip_center_x = body_center_x[min(hip_y, len(body_center_x)-1)]
        hip_width = int(estimate_width_at_height(body_mask, hip_y) * 0.8)
        landmarks['left_hip'] = (hip_center_x - hip_width//2, hip_y)
        landmarks['right_hip'] = (hip_center_x + hip_width//2, hip_y)
        landmarks['hip_center'] = (hip_center_x, hip_y)
        
        # Knees
        knee_y = body_top + int(body_height * 0.75)
        knee_center_x = body_center_x[min(knee_y, len(body_center_x)-1)]
        knee_width = int(estimate_width_at_height(body_mask, knee_y) * 0.6)
        landmarks['left_knee'] = (knee_center_x - knee_width//2, knee_y)
        landmarks['right_knee'] = (knee_center_x + knee_width//2, knee_y)
        
        # Ankles
        ankle_y = body_top + int(body_height * 0.92)
        ankle_center_x = body_center_x[min(ankle_y, len(body_center_x)-1)]
        ankle_width = int(estimate_width_at_height(body_mask, ankle_y) * 0.4)
        landmarks['left_ankle'] = (ankle_center_x - ankle_width//2, ankle_y)
        landmarks['right_ankle'] = (ankle_center_x + ankle_width//2, ankle_y)
    else:
        # Fallback proportions
        center_x = width // 2
        landmarks = {
            'skull': (center_x, int(height * 0.08)),
            'left_shoulder': (center_x - int(width * 0.12), int(height * 0.18)),
            'right_shoulder': (center_x + int(width * 0.12), int(height * 0.18)),
            'shoulder_center': (center_x, int(height * 0.18)),
            'left_hip': (center_x - int(width * 0.08), int(height * 0.50)),
            'right_hip': (center_x + int(width * 0.08), int(height * 0.50)),
            'hip_center': (center_x, int(height * 0.50)),
            'left_knee': (center_x - int(width * 0.06), int(height * 0.75)),
            'right_knee': (center_x + int(width * 0.06), int(height * 0.75)),
            'left_ankle': (center_x - int(width * 0.04), int(height * 0.92)),
            'right_ankle': (center_x + int(width * 0.04), int(height * 0.92))
        }
    
    return landmarks

def calculate_clinical_measurements(landmarks, width, height):
    """Calculate clinical measurements from landmarks"""
    measurements = {}
    
    # Head alignment
    skull_x = landmarks['skull'][0]
    shoulder_center_x = landmarks['shoulder_center'][0]
    head_forward_distance = abs(skull_x - shoulder_center_x)
    measurements['head_alignment'] = (head_forward_distance / width) * 100
    
    # Shoulder symmetry
    left_shoulder_y = landmarks['left_shoulder'][1]
    right_shoulder_y = landmarks['right_shoulder'][1]
    shoulder_height_diff = abs(left_shoulder_y - right_shoulder_y)
    measurements['shoulder_symmetry'] = (shoulder_height_diff / height) * 100
    
    # Hip symmetry
    left_hip_y = landmarks['left_hip'][1]
    right_hip_y = landmarks['right_hip'][1]
    hip_height_diff = abs(left_hip_y - right_hip_y)
    measurements['hip_symmetry'] = (hip_height_diff / height) * 100
    
    # Vertical alignment
    hip_center_x = landmarks['hip_center'][0]
    vertical_offset = abs(shoulder_center_x - hip_center_x)
    measurements['vertical_alignment'] = (vertical_offset / width) * 100
    
    return measurements

def calculate_head_score(head_alignment_percent):
    """Calculate head position score"""
    if head_alignment_percent <= 2:
        return 4
    elif head_alignment_percent <= 4:
        return 3
    elif head_alignment_percent <= 7:
        return 2
    else:
        return 1

def calculate_shoulder_score(shoulder_asymmetry_percent):
    """Calculate shoulder score"""
    if shoulder_asymmetry_percent <= 1:
        return 4
    elif shoulder_asymmetry_percent <= 2:
        return 3
    elif shoulder_asymmetry_percent <= 4:
        return 2
    else:
        return 1

def calculate_hip_score(hip_asymmetry_percent):
    """Calculate hip score"""
    if hip_asymmetry_percent <= 1:
        return 4
    elif hip_asymmetry_percent <= 2:
        return 3
    elif hip_asymmetry_percent <= 3:
        return 2
    else:
        return 1

def calculate_alignment_score(vertical_alignment_percent):
    """Calculate alignment score"""
    if vertical_alignment_percent <= 3:
        return 4
    elif vertical_alignment_percent <= 5:
        return 3
    elif vertical_alignment_percent <= 8:
        return 2
    else:
        return 1

def generate_detailed_assessments(analysis):
    """Generate detailed assessments"""
    assessments = {}
    measurements = analysis['measurements']
    
    # Head assessment
    head_score = analysis['head_score']
    head_measurement = measurements['head_alignment']
    if head_score >= 4:
        assessments['head_assessment'] = f"Excellent head positioning ({head_measurement:.1f}% forward)"
        assessments['head_color'] = "🟢"
    elif head_score >= 3:
        assessments['head_assessment'] = f"Good head alignment ({head_measurement:.1f}% forward)"
        assessments['head_color'] = "🟡"
    elif head_score >= 2:
        assessments['head_assessment'] = f"Moderate forward head posture ({head_measurement:.1f}% forward)"
        assessments['head_color'] = "🟠"
    else:
        assessments['head_assessment'] = f"Significant forward head posture ({head_measurement:.1f}% forward)"
        assessments['head_color'] = "🔴"
    
    # Shoulder assessment
    shoulder_score = analysis['shoulder_score']
    shoulder_measurement = measurements['shoulder_symmetry']
    if shoulder_score >= 4:
        assessments['shoulder_assessment'] = f"Excellent shoulder alignment ({shoulder_measurement:.1f}% difference)"
        assessments['shoulder_color'] = "🟢"
    elif shoulder_score >= 3:
        assessments['shoulder_assessment'] = f"Good shoulder positioning ({shoulder_measurement:.1f}% difference)"
        assessments['shoulder_color'] = "🟡"
    elif shoulder_score >= 2:
        assessments['shoulder_assessment'] = f"Moderate shoulder asymmetry ({shoulder_measurement:.1f}% difference)"
        assessments['shoulder_color'] = "🟠"
    else:
        assessments['shoulder_assessment'] = f"Significant shoulder imbalance ({shoulder_measurement:.1f}% difference)"
        assessments['shoulder_color'] = "🔴"
    
    # Hip assessment
    hip_score = analysis['hip_score']
    hip_measurement = measurements['hip_symmetry']
    if hip_score >= 4:
        assessments['hip_assessment'] = f"Excellent hip alignment ({hip_measurement:.1f}% difference)"
        assessments['hip_color'] = "🟢"
    elif hip_score >= 3:
        assessments['hip_assessment'] = f"Good hip positioning ({hip_measurement:.1f}% difference)"
        assessments['hip_color'] = "🟡"
    elif hip_score >= 2:
        assessments['hip_assessment'] = f"Moderate hip asymmetry ({hip_measurement:.1f}% difference)"
        assessments['hip_color'] = "🟠"
    else:
        assessments['hip_assessment'] = f"Significant hip imbalance ({hip_measurement:.1f}% difference)"
        assessments['hip_color'] = "🔴"
    
    # Alignment assessment
    alignment_score = analysis['alignment_score']
    alignment_measurement = measurements['vertical_alignment']
    if alignment_score >= 4:
        assessments['alignment_assessment'] = f"Excellent overall alignment ({alignment_measurement:.1f}% offset)"
        assessments['alignment_color'] = "🟢"
    elif alignment_score >= 3:
        assessments['alignment_assessment'] = f"Good vertical alignment ({alignment_measurement:.1f}% offset)"
        assessments['alignment_color'] = "🟡"
    elif alignment_score >= 2:
        assessments['alignment_assessment'] = f"Moderate alignment issues ({alignment_measurement:.1f}% offset)"
        assessments['alignment_color'] = "🟠"
    else:
        assessments['alignment_assessment'] = f"Poor overall alignment ({alignment_measurement:.1f}% offset)"
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

def create_annotated_image(image_array, landmarks, analysis):
    """Create image with clinical measurement dots and lines"""
    if image_array.dtype != np.uint8:
        image_array = (image_array * 255).astype(np.uint8)
    
    pil_image = Image.fromarray(image_array)
    draw = ImageDraw.Draw(pil_image)
    
    # Color coding
    colors = {
        'excellent': '#00FF00',
        'good': '#90EE90',
        'fair': '#FFD700',
        'poor': '#FFA500',
        'very_poor': '#FF0000'
    }
    
    # Dot size
    dot_size = max(8, min(20, image_array.shape[1] // 80))
    line_width = max(2, dot_size // 4)
    
    # Draw reference lines
    skull_pos = landmarks.get('skull', (0, 0))
    ankle_center = ((landmarks['left_ankle'][0] + landmarks['right_ankle'][0])//2, 
                    (landmarks['left_ankle'][1] + landmarks['right_ankle'][1])//2)
    
    draw.line([skull_pos, ankle_center], fill='#FFFFFF', width=2)
    
    # Horizontal reference lines
    shoulder_y = landmarks['shoulder_center'][1]
    hip_y = landmarks['hip_center'][1]
    
    draw.line([(0, shoulder_y), (image_array.shape[1], shoulder_y)], fill='#CCCCCC', width=1)
    draw.line([(0, hip_y), (image_array.shape[1], hip_y)], fill='#CCCCCC', width=1)
    
    # Color function
    def get_score_color(score):
        if score >= 4:
            return colors['excellent']
        elif score >= 3:
            return colors['good']
        elif score >= 2:
            return colors['fair']
        else:
            return colors['poor']
    
    # Draw landmarks
    landmarks_to_draw = [
        ('skull', 'Head Position', analysis.get('head_score', 2)),
        ('left_shoulder', 'L Shoulder', analysis.get('shoulder_score', 2)),
        ('right_shoulder', 'R Shoulder', analysis.get('shoulder_score', 2)),
        ('left_hip', 'L Hip', analysis.get('hip_score', 2)),
        ('right_hip', 'R Hip', analysis.get('hip_score', 2)),
        ('left_knee', 'L Knee', analysis.get('alignment_score', 2)),
        ('right_knee', 'R Knee', analysis.get('alignment_score', 2)),
        ('left_ankle', 'L Ankle', analysis.get('alignment_score', 2)),
        ('right_ankle', 'R Ankle', analysis.get('alignment_score', 2))
    ]
    
    for landmark_key, label, score in landmarks_to_draw:
        if landmark_key in landmarks:
            pos = landmarks[landmark_key]
            color = get_score_color(score)
            
            # Draw outer circle
            draw.ellipse([
                pos[0] - dot_size - 2, pos[1] - dot_size - 2,
                pos[0] + dot_size + 2, pos[1] + dot_size + 2
            ], fill='#FFFFFF')
            
            # Draw inner circle
            draw.ellipse([
                pos[0] - dot_size, pos[1] - dot_size,
                pos[0] + dot_size, pos[1] + dot_size
            ], fill=color)
            
            # Draw center dot
            center_size = dot_size // 3
            draw.ellipse([
                pos[0] - center_size, pos[1] - center_size,
                pos[0] + center_size, pos[1] + center_size
            ], fill='#000000')
    
    # Draw symmetry lines
    draw.line([landmarks['left_shoulder'], landmarks['right_shoulder']], 
              fill=get_score_color(analysis.get('shoulder_score', 2)), width=line_width)
    
    draw.line([landmarks['left_hip'], landmarks['right_hip']], 
              fill=get_score_color(analysis.get('hip_score', 2)), width=line_width)
    
    return pil_image

def analyze_posture(image_array):
    """Main posture analysis function"""
    height, width = image_array.shape[:2]
    
    # Get landmarks
    landmarks = estimate_anatomical_landmarks(image_array)
    
    # Calculate measurements
    measurements = calculate_clinical_measurements(landmarks, width, height)
    
    # Calculate scores
    head_score = calculate_head_score(measurements['head_alignment'])
    shoulder_score = calculate_shoulder_score(measurements['shoulder_symmetry'])
    hip_score = calculate_hip_score(measurements['hip_symmetry'])
    alignment_score = calculate_alignment_score(measurements['vertical_alignment'])
    
    # Total score
    total_score = head_score + shoulder_score + hip_score + alignment_score
    overall_percentage = (total_score / 16) * 100
    
    # Build analysis
    analysis = {
        'total_score': total_score,
        'max_score': 16,
        'percentage': overall_percentage,
        'head_score': head_score,
        'shoulder_score': shoulder_score,
        'hip_score': hip_score,
        'alignment_score': alignment_score,
        'landmarks': landmarks,
        'measurements': measurements
    }
    
    # Add assessments
    analysis.update(generate_detailed_assessments(analysis))
    
    return analysis

def generate_exercise_recommendations(analysis):
    """Generate exercise recommendations"""
    recommendations = []
    
    if analysis.get('head_score', 4) < 3:
        recommendations.extend([
            "**🎯 Head & Neck Correction Program:**",
            "• Chin tucks: 3 sets of 15 holds (5 seconds each)",
            "• Deep cervical flexor strengthening",
            "• Upper trap stretches: 3 x 30 seconds",
            "• Postural awareness training",
            ""
        ])
    
    if analysis.get('shoulder_score', 4) < 3:
        recommendations.extend([
            "**💪 Shoulder Symmetry Program:**",
            "• Unilateral strengthening for weaker side",
            "• Shoulder blade squeezes: 3 sets of 15",
            "• Single-arm rows: 2 sets of 12 (weaker side)",
            "• Thoracic spine mobility exercises",
            ""
        ])
    
    if analysis.get('hip_score', 4) < 3:
        recommendations.extend([
            "**🔥 Hip Alignment Program:**",
            "• Unilateral glute strengthening",
            "• Side-lying hip abduction: 3 sets of 15",
            "• Hip flexor stretches: 3 x 30 seconds",
            "• Pelvic leveling exercises",
            ""
        ])
    
    if analysis.get('alignment_score', 4) < 3:
        recommendations.extend([
            "**⚖️ Postural Alignment Program:**",
            "• Core stabilization exercises",
            "• Wall posture training: 3 x 2 minutes",
            "• Plank progressions: 3 x 30 seconds",
            "• Movement pattern retraining",
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

def save_analysis_data(analysis_data, patient_name):
    """Save analysis to session state"""
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
        "analysis_type": "Clinical CV Analysis"
    }
    
    st.session_state.posture_analyses.append(save_data)
    return True

def create_clickable_image_interface(image_array):
    """Create an interactive interface for manual landmark placement"""
    height, width = image_array.shape[:2]
    
    # Convert to base64 for HTML display
    pil_image = Image.fromarray(image_array.astype(np.uint8))
    
    # Resize image if it's too large to fit properly
    max_height = 1200  # Increased from 800 to 1200
    if height > max_height:
        scale_factor = max_height / height
        new_width = int(width * scale_factor)
        new_height = max_height
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    else:
        new_width = width
        new_height = height
    
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Create the interactive HTML interface
    html_interface = f"""
    <div style="position: relative; display: inline-block; border: 2px solid #0066cc; border-radius: 10px; overflow: auto; width: 100%; max-width: 900px; max-height: 1200px; margin: 0 auto;">
        <img id="postureImage" src="data:image/png;base64,{img_base64}" 
             style="width: 100%; height: auto; display: block; cursor: crosshair;"
             onclick="placeLandmark(event)">
        
        <div id="landmarks" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
        </div>
        
        <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; font-size: 12px;">
            <div><strong>Click to place landmarks:</strong></div>
            <div id="currentLandmark" style="color: #00ff00; font-weight: bold;">1. Skull/Head</div>
            <div style="margin-top: 5px;">
                <button onclick="resetLandmarks()" style="background: #ff4444; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin-right: 5px;">Reset</button>
                <button onclick="undoLast()" style="background: #ffaa00; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Undo</button>
            </div>
        </div>
    </div>
    
    <div style="margin-top: 15px; padding: 15px; background-color: rgba(0, 0, 0, 0.2); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2);">
        <h4 style="color: #0066cc; margin-top: 0;">📍 Landmark Placement Guide:</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px; color: inherit;">
            <div><strong>1. Skull/Head:</strong> Top of head or ear level</div>
            <div><strong>2. Left Shoulder:</strong> Acromion process (left side)</div>
            <div><strong>3. Right Shoulder:</strong> Acromion process (right side)</div>
            <div><strong>4. Left Hip:</strong> Greater trochanter (left side)</div>
            <div><strong>5. Right Hip:</strong> Greater trochanter (right side)</div>
            <div><strong>6. Left Knee:</strong> Lateral femoral condyle</div>
            <div><strong>7. Right Knee:</strong> Lateral femoral condyle</div>
            <div><strong>8. Left Ankle:</strong> Lateral malleolus</div>
            <div><strong>9. Right Ankle:</strong> Lateral malleolus</div>
        </div>
        <div style="margin-top: 10px; font-size: 12px; color: inherit; opacity: 0.8;">
            💡 <strong>Tip:</strong> Click directly on the anatomical landmarks. The system will calculate measurements once all 9 points are placed.
        </div>
    </div>
    
    <script>
    let landmarkCount = 0;
    let landmarks = [];
    const landmarkNames = [
        'skull', 'left_shoulder', 'right_shoulder', 'left_hip', 'right_hip',
        'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
    ];
    const landmarkLabels = [
        '1. Skull/Head', '2. Left Shoulder', '3. Right Shoulder', '4. Left Hip', '5. Right Hip',
        '6. Left Knee', '7. Right Knee', '8. Left Ankle', '9. Right Ankle'
    ];
    const landmarkColors = ['#ff0000', '#00ff00', '#00ff00', '#0000ff', '#0000ff', '#ffff00', '#ffff00', '#ff8800', '#ff8800'];
    
    function placeLandmark(event) {{
        if (landmarkCount >= 9) return;
        
        const rect = event.target.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width * {width}).toFixed(0);
        const y = ((event.clientY - rect.top) / rect.height * {height}).toFixed(0);
        
        landmarks.push({{
            name: landmarkNames[landmarkCount],
            x: parseInt(x),
            y: parseInt(y),
            color: landmarkColors[landmarkCount]
        }});
        
        addLandmarkDot(event.clientX - rect.left, event.clientY - rect.top, landmarkColors[landmarkCount], landmarkCount + 1);
        landmarkCount++;
        
        updateCurrentLandmark();
        
        if (landmarkCount === 9) {{
            document.getElementById('currentLandmark').innerHTML = '✅ All landmarks placed! Click Calculate below.';
            // Store landmarks in Streamlit session state
            window.parent.postMessage({{
                type: 'landmarks_complete',
                landmarks: landmarks
            }}, '*');
        }}
    }}
    
    function addLandmarkDot(x, y, color, number) {{
        const landmarksDiv = document.getElementById('landmarks');
        const dot = document.createElement('div');
        dot.style.position = 'absolute';
        dot.style.left = (x - 8) + 'px';
        dot.style.top = (y - 8) + 'px';
        dot.style.width = '16px';
        dot.style.height = '16px';
        dot.style.borderRadius = '50%';
        dot.style.backgroundColor = color;
        dot.style.border = '2px solid white';
        dot.style.color = 'white';
        dot.style.fontSize = '10px';
        dot.style.fontWeight = 'bold';
        dot.style.display = 'flex';
        dot.style.alignItems = 'center';
        dot.style.justifyContent = 'center';
        dot.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
        dot.innerHTML = number;
        dot.id = 'landmark_' + number;
        landmarksDiv.appendChild(dot);
    }}
    
    function updateCurrentLandmark() {{
        if (landmarkCount < 9) {{
            document.getElementById('currentLandmark').innerHTML = landmarkLabels[landmarkCount];
        }}
    }}
    
    function resetLandmarks() {{
        landmarks = [];
        landmarkCount = 0;
        document.getElementById('landmarks').innerHTML = '';
        updateCurrentLandmark();
        window.parent.postMessage({{type: 'landmarks_reset'}}, '*');
    }}
    
    function undoLast() {{
        if (landmarkCount > 0) {{
            landmarks.pop();
            landmarkCount--;
            document.getElementById('landmark_' + (landmarkCount + 1)).remove();
            updateCurrentLandmark();
        }}
    }}
    </script>
    """
    
    return html_interface

def process_manual_landmarks(manual_landmarks):
    """Process manually placed landmarks"""
    landmarks = {}
    
    for landmark in manual_landmarks:
        landmarks[landmark['name']] = (landmark['x'], landmark['y'])
    
    # Calculate centers
    if 'left_shoulder' in landmarks and 'right_shoulder' in landmarks:
        left_s = landmarks['left_shoulder']
        right_s = landmarks['right_shoulder']
        landmarks['shoulder_center'] = ((left_s[0] + right_s[0])//2, (left_s[1] + right_s[1])//2)
    
    if 'left_hip' in landmarks and 'right_hip' in landmarks:
        left_h = landmarks['left_hip']
        right_h = landmarks['right_hip']
        landmarks['hip_center'] = ((left_h[0] + right_h[0])//2, (left_h[1] + right_h[1])//2)
    
    return landmarks

# Custom CSS
st.markdown("""
<style>
.stCamera > div {
    width: 100% !important;
    max-width: 800px !important;
}
.stCamera > div > div {
    width: 100% !important;
    height: 500px !important;
    aspect-ratio: 16/10 !important;
}
.stCamera > div > div > div > video {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    border-radius: 10px !important;
    border: 2px solid #0066cc !important;
}
</style>
""", unsafe_allow_html=True)

# Main App
st.title("🏥 AI Clinical Assistant")
st.markdown("### *Visual Posture Analysis with Clinical Measurement Dots*")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Clinical Analysis Settings")
    
    patient_name = st.text_input("Patient Name", value="Anonymous")
    
    analysis_mode = st.selectbox(
        "📊 Analysis Mode",
        ["Upload Image", "Take Photo (Vertical Full-Body)", "Manual Landmark Placement"]
    )
    
    st.markdown("---")
    st.header("📋 Clinical Instructions")
    st.markdown("""
    **For optimal clinical analysis:**
    
    📸 **Photo Setup:**
    - **Side view positioning** (90° to camera)
    - Full body visible (head to feet)
    - Arms relaxed at sides
    - Natural standing position
    - Good lighting, plain background
    
    🎯 **Measurement Points:**
    - 🔴 **Red dots:** Poor alignment (Score 1)
    - 🟠 **Orange dots:** Fair alignment (Score 2) 
    - 🟡 **Yellow dots:** Good alignment (Score 3)
    - 🟢 **Green dots:** Excellent alignment (Score 4)
    """)

# Main content columns
col1, col2 = st.columns([3, 2])

# Left column - Image upload/capture
with col1:
    st.header("📸 Clinical Posture Analysis")
    
    if analysis_mode == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload a side-view photo for clinical analysis",
            type=['jpg', 'jpeg', 'png'],
            help="Best results with side-view, full-body photos"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            # Analyze posture
            with st.spinner("🔍 Performing clinical analysis..."):
                analysis = analyze_posture(image_array)
                # Store in session state for display
                st.session_state.current_analysis = analysis
            
            # Create annotated image
            annotated_image = create_annotated_image(image_array, analysis['landmarks'], analysis)
            
            # Display images
            img_col1, img_col2 = st.columns(2)
            with img_col1:
                st.image(image, caption="📷 Original Photo", use_container_width=True)
            with img_col2:
                st.image(annotated_image, caption="🎯 Clinical Measurement Points", use_container_width=True)
        else:
            st.info("👆 Please upload an image to begin analysis")
    
    elif analysis_mode == "Take Photo (Vertical Full-Body)":
        st.info("📷 Camera optimized for vertical full-body capture")
        st.markdown("**Instructions:** Stand facing or sideways to camera, full body visible in vertical frame")
        
        picture = st.camera_input("Take a side-view photo for clinical analysis")
        
        if picture is not None:
            image = Image.open(picture)
            image_array = np.array(image)
            
            # Analyze posture
            with st.spinner("🔍 Performing clinical analysis..."):
                analysis = analyze_posture(image_array)
                # Store in session state for display
                st.session_state.current_analysis = analysis
            
            # Create annotated image
            annotated_image = create_annotated_image(image_array, analysis['landmarks'], analysis)
            
            # Display result
            st.image(annotated_image, caption="🎯 Your Clinical Analysis", use_column_width=True)
    
    elif analysis_mode == "Manual Landmark Placement":
        st.header("🎯 Manual Clinical Landmark Placement")
        st.info("📍 Click directly on anatomical landmarks for precise clinical measurement")
        
        uploaded_file = st.file_uploader(
            "Upload photo for manual landmark placement",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear side-view photo for precise landmark placement",
            key="manual_upload"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            # Display interactive interface
            st.markdown("### 📍 Click on the image to place landmarks:")
            
            # Create clickable interface
            html_interface = create_clickable_image_interface(image_array)
            st.components.v1.html(html_interface, height=1400, scrolling=True)
            
            # Calculate button appears immediately after the image interface
            st.markdown("---")
            
            # Info message about using manual coordinates
            st.info("⚠️ **Note:** The clickable interface is for visualization only. Please use the 'Manual Coordinate Entry' section below to enter the landmark positions you've identified, then click 'Use Manual Coordinates' followed by 'Calculate Clinical Analysis'.")
            
            # Reset button
            if st.button("🔄 Reset View", use_container_width=True, key="reset_view"):
                st.session_state.manual_landmarks = None
                st.session_state.landmarks_placed = False
                st.rerun()
            
            # Manual landmark input as backup
            st.markdown("---")
            st.markdown("### 🔧 Manual Coordinate Entry")
            st.warning("📝 **Required:** After clicking landmarks above, enter their coordinates here to proceed with analysis")
            
            # Manual landmark input
            with st.form("landmark_coordinates_form"):
                st.info("Look at the clicked landmarks above and enter their approximate pixel coordinates below")
                
                coords_col1, coords_col2, coords_col3 = st.columns(3)
                
                manual_coords = {}
                landmarks_list = [
                    ('skull', 'Skull/Head', 'red'),
                    ('left_shoulder', 'Left Shoulder', 'green'),
                    ('right_shoulder', 'Right Shoulder', 'green'),
                    ('left_hip', 'Left Hip', 'blue'),
                    ('right_hip', 'Right Hip', 'blue'),
                    ('left_knee', 'Left Knee', 'yellow'),
                    ('right_knee', 'Right Knee', 'yellow'),
                    ('left_ankle', 'Left Ankle', 'orange'),
                    ('right_ankle', 'Right Ankle', 'orange')
                ]
                
                for i, (key, label, color) in enumerate(landmarks_list):
                    col = [coords_col1, coords_col2, coords_col3][i % 3]
                    with col:
                        st.markdown(f"**{label}** <span style='color: {color};'>●</span>", unsafe_allow_html=True)
                        x = st.number_input(f"X", key=f"{key}_x", min_value=0, max_value=image_array.shape[1], value=0)
                        y = st.number_input(f"Y", key=f"{key}_y", min_value=0, max_value=image_array.shape[0], value=0)
                        manual_coords[key] = (int(x), int(y))
                
                submitted = st.form_submit_button("✅ Confirm Coordinates & Analyze", use_container_width=True, type="primary")
                
                if submitted:
                    # Check if all coordinates are set (not all zeros)
                    if all(coords != (0, 0) for coords in manual_coords.values()):
                        st.session_state.manual_landmarks = [
                            {'name': key, 'x': coords[0], 'y': coords[1]} 
                            for key, coords in manual_coords.items()
                        ]
                        st.session_state.landmarks_placed = True
                        
                        # Process manual landmarks immediately
                        with st.spinner("🔍 Calculating clinical measurements..."):
                            landmarks = process_manual_landmarks(st.session_state.manual_landmarks)
                            
                            # Calculate measurements
                            measurements = calculate_clinical_measurements(landmarks, image_array.shape[1], image_array.shape[0])
                            
                            # Calculate scores
                            head_score = calculate_head_score(measurements['head_alignment'])
                            shoulder_score = calculate_shoulder_score(measurements['shoulder_symmetry'])
                            hip_score = calculate_hip_score(measurements['hip_symmetry'])
                            alignment_score = calculate_alignment_score(measurements['vertical_alignment'])
                            
                            # Total score
                            total_score = head_score + shoulder_score + hip_score + alignment_score
                            overall_percentage = (total_score / 16) * 100
                            
                            # Build analysis
                            analysis = {
                                'total_score': total_score,
                                'max_score': 16,
                                'percentage': overall_percentage,
                                'head_score': head_score,
                                'shoulder_score': shoulder_score,
                                'hip_score': hip_score,
                                'alignment_score': alignment_score,
                                'landmarks': landmarks,
                                'measurements': measurements
                            }
                            
                            # Add assessments
                            analysis.update(generate_detailed_assessments(analysis))
                            
                            # Store analysis for display
                            st.session_state.current_analysis = analysis
                        
                        # Create annotated image
                        annotated_image = create_annotated_image(image_array, landmarks, analysis)
                        
                        # Display results
                        st.success("✅ Clinical analysis completed!")
                        
                        # Display images side by side
                        st.markdown("### 📊 Analysis Results")
                        img_col1, img_col2 = st.columns(2)
                        with img_col1:
                            st.image(image, caption="📷 Original Photo", use_container_width=True)
                        with img_col2:
                            st.image(annotated_image, caption="🎯 Manual Landmark Analysis", use_container_width=True)
                    else:
                        st.error("❌ Please enter valid coordinates for all landmarks (not all zeros)")

# Right column - Analysis results
with col2:
    # Check if we have an analysis to display from session state
    if 'current_analysis' in st.session_state and st.session_state.current_analysis is not None:
        analysis = st.session_state.current_analysis
        
        st.markdown("## 📊 Clinical Analysis")
        
        # Display score in a clear way
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background-color: rgba(0, 0, 0, 0.1); border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <h2 style="margin: 0; color: inherit;">Clinical Posture Score</h2>
            <h1 style="margin: 10px 0; font-size: 48px; color: inherit;">{analysis['total_score']}/16</h1>
            <p style="margin: 0; font-size: 24px; color: #28a745;">↑ {analysis['percentage']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(analysis['percentage'] / 100)
        
        # Overall status
        if analysis['overall_color'] == 'success':
            st.success(f"✅ {analysis['overall']}")
        elif analysis['overall_color'] == 'info':
            st.info(f"ℹ️ {analysis['overall']}")
        elif analysis['overall_color'] == 'warning':
            st.warning(f"⚠️ {analysis['overall']}")
        else:
            st.error(f"❌ {analysis['overall']}")
        
        st.markdown(f"""
        <div style="text-align: center; padding: 15px; background-color: rgba(0, 0, 0, 0.1); border-radius: 10px; margin: 20px 0; border: 1px solid rgba(255, 255, 255, 0.1);">
            <h3 style="margin: 0; color: inherit;">Clinical Risk Level</h3>
            <h2 style="margin: 10px 0; color: inherit;">{analysis['risk_level']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed measurements
        with st.expander("📏 Clinical Measurements", expanded=True):
            measurements = analysis['measurements']
            
            # Create a nice layout for measurements
            st.markdown(f"""
            <div style="padding: 10px; background-color: transparent;">
                <p style="color: inherit;">{analysis['head_color']} <strong>Head Position:</strong> {analysis['head_assessment']}</p>
                <p style="color: inherit;">{analysis['shoulder_color']} <strong>Shoulders:</strong> {analysis['shoulder_assessment']}</p>
                <p style="color: inherit;">{analysis['hip_color']} <strong>Hips:</strong> {analysis['hip_assessment']}</p>
                <p style="color: inherit;">{analysis['alignment_color']} <strong>Alignment:</strong> {analysis['alignment_assessment']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📊 Raw Measurements")
            
            # Two column layout for measurements
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"**Head forward:** {measurements['head_alignment']:.1f}%")
                st.markdown(f"**Shoulder asymmetry:** {measurements['shoulder_symmetry']:.1f}%")
            with m2:
                st.markdown(f"**Hip asymmetry:** {measurements['hip_symmetry']:.1f}%")
                st.markdown(f"**Vertical offset:** {measurements['vertical_alignment']:.1f}%")
        
        # Save button
        st.markdown("---")
        if st.button("💾 Save Clinical Analysis", use_container_width=True, key="save_main"):
            if save_analysis_data(analysis, patient_name):
                st.success("✅ Clinical analysis saved!")
                st.balloons()
        
        # Exercise recommendations
        st.markdown("---")
        st.subheader("💪 Clinical Exercise Prescription")
        st.markdown("*Based on quantified postural measurements*")
        
        recommendations = generate_exercise_recommendations(analysis)
        
        for rec in recommendations:
            if rec.startswith("**") and rec.endswith("**"):
                st.markdown(rec)
            elif rec == "":
                st.markdown("")
            else:
                st.markdown(f"• {rec}")
    else:
        # Show placeholder when no analysis
        st.markdown("""
        <div style="text-align: center; padding: 50px; background-color: rgba(0, 0, 0, 0.1); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <h3 style="color: inherit;">📊 Clinical Analysis</h3>
            <p style="color: inherit;">Results will appear here after analysis</p>
        </div>
        """, unsafe_allow_html=True)

# Progress tracking section - outside of columns
st.markdown("---")

if len(st.session_state.posture_analyses) > 0:
    st.header("📈 Clinical Progress Tracking")
    
    analyses = st.session_state.posture_analyses
    df = pd.DataFrame(analyses)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Clinical Analyses", len(df))
    with col2:
        st.metric("Average Score", f"{df['percentage'].mean():.1f}%")
    with col3:
        st.metric("Latest Score", f"{df['percentage'].iloc[-1]:.1f}%")
    with col4:
        if len(df) > 1:
            improvement = df['percentage'].iloc[-1] - df['percentage'].iloc[0]
            st.metric("Clinical Progress", f"{improvement:+.1f}%")
        else:
            st.metric("Clinical Progress", "Baseline")
    
    # Recent analyses
    st.subheader("📋 Clinical Session Data")
    display_df = df[['timestamp', 'patient', 'total_score', 'percentage', 'overall_assessment']]
    st.dataframe(display_df, use_container_width=True)

# Clinical legend
st.markdown("---")
st.header("🎯 Clinical Measurement Legend")
legend_col1, legend_col2 = st.columns(2)

with legend_col1:
    st.markdown("""
    **📍 Measurement Points:**
    - **Skull:** Head position assessment
    - **Shoulders:** Left/right symmetry
    - **Hips:** Pelvic level evaluation 
    - **Knees:** Lower limb alignment
    - **Ankles:** Base of support
    """)

with legend_col2:
    st.markdown("""
    **🎨 Color Coding:**
    - 🟢 **Green:** Excellent (Score 4)
    - 🟡 **Yellow:** Good (Score 3)
    - 🟠 **Orange:** Fair (Score 2)
    - 🔴 **Red:** Poor (Score 1)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: inherit; opacity: 0.7; font-size: 14px;'>
💙 <strong>AI Clinical Assistant</strong> • Visual posture analysis with clinical measurement validation<br>
Quantified assessment • Evidence-based scoring • Professional documentation
</div>
""", unsafe_allow_html=True)
