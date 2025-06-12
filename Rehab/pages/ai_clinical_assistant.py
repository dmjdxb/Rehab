import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
import math
from datetime import datetime
import pandas as pd
import os
import base64
import io

# Try to import scipy for better image processing
try:
    from scipy import ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

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

def estimate_anatomical_landmarks(image_array):
    """Estimate key anatomical landmarks using improved body detection"""
    height, width = image_array.shape[:2]
    
    # Convert to grayscale
    if len(image_array.shape) == 3:
        gray = np.mean(image_array, axis=2).astype(np.uint8)
    else:
        gray = image_array
    
    # Find the actual body region using skin tone and contrast detection
    body_mask = detect_body_region(image_array)
    body_center_x = find_body_centerline(body_mask, height)
    
    # Use anatomical proportions relative to detected body region
    landmarks = {}
    
    # Find body boundaries
    body_top, body_bottom, body_left, body_right = find_body_boundaries(body_mask)
    
    if body_top is not None and body_bottom is not None:
        body_height = body_bottom - body_top
        
        # Head/Skull - at body top + head proportion
        head_y = body_top + int(body_height * 0.12)  # 12% down from body top
        head_x = body_center_x[min(head_y, len(body_center_x)-1)]
        landmarks['skull'] = (head_x, head_y)
        
        # Shoulders - anatomical shoulder line
        shoulder_y = body_top + int(body_height * 0.20)  # 20% down from body top
        shoulder_center_x = body_center_x[min(shoulder_y, len(body_center_x)-1)]
        shoulder_width = estimate_shoulder_width(body_mask, shoulder_y)
        landmarks['left_shoulder'] = (shoulder_center_x - shoulder_width//2, shoulder_y)
        landmarks['right_shoulder'] = (shoulder_center_x + shoulder_width//2, shoulder_y)
        landmarks['shoulder_center'] = (shoulder_center_x, shoulder_y)
        
        # Hips - anatomical hip line  
        hip_y = body_top + int(body_height * 0.55)  # 55% down from body top
        hip_center_x = body_center_x[min(hip_y, len(body_center_x)-1)]
        hip_width = estimate_hip_width(body_mask, hip_y)
        landmarks['left_hip'] = (hip_center_x - hip_width//2, hip_y)
        landmarks['right_hip'] = (hip_center_x + hip_width//2, hip_y)
        landmarks['hip_center'] = (hip_center_x, hip_y)
        
        # Knees - anatomical knee line
        knee_y = body_top + int(body_height * 0.75)  # 75% down from body top
        knee_center_x = body_center_x[min(knee_y, len(body_center_x)-1)]
        knee_width = estimate_knee_width(body_mask, knee_y)
        landmarks['left_knee'] = (knee_center_x - knee_width//2, knee_y)
        landmarks['right_knee'] = (knee_center_x + knee_width//2, knee_y)
        
        # Ankles - anatomical ankle line
        ankle_y = body_top + int(body_height * 0.92)  # 92% down from body top
        ankle_center_x = body_center_x[min(ankle_y, len(body_center_x)-1)]
        ankle_width = estimate_ankle_width(body_mask, ankle_y)
        landmarks['left_ankle'] = (ankle_center_x - ankle_width//2, ankle_y)
        landmarks['right_ankle'] = (ankle_center_x + ankle_width//2, ankle_y)
    
    else:
        # Enhanced fallback using image analysis
        landmarks = create_proportional_landmarks(image_array, width, height)
    
    return landmarks

def detect_body_region(image_array):
    """Detect the actual body region, excluding shadows and background"""
    height, width = image_array.shape[:2]
    
    # Convert to different color spaces for better body detection
    if len(image_array.shape) == 3:
        # RGB analysis
        r, g, b = image_array[:,:,0], image_array[:,:,1], image_array[:,:,2]
        
        # Skin tone detection (rough approximation)
        skin_mask = ((r > 95) & (g > 40) & (b > 20) & 
                    (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b) > 15) &
                    (np.abs(r - g) > 15) & (r > g) & (r > b))
        
        # Clothing detection (non-skin regions with moderate contrast)
        gray = np.mean(image_array, axis=2)
        clothing_mask = ((gray > 30) & (gray < 200) & ~skin_mask)
        
        # Combine skin and clothing for body detection
        body_mask = skin_mask | clothing_mask
        
        # Remove small isolated regions (likely shadows/noise)
        if SCIPY_AVAILABLE:
            from scipy import ndimage
            body_mask = ndimage.binary_opening(body_mask, structure=np.ones((5,5)))
            body_mask = ndimage.binary_closing(body_mask, structure=np.ones((10,10)))
        else:
            # Simple noise reduction without scipy
            # Erode then dilate to remove small noise
            kernel = np.ones((3,3), np.uint8)
            body_mask = binary_erosion(body_mask, kernel)
            body_mask = binary_dilation(body_mask, kernel)
        
    else:
        # Fallback for grayscale
        gray = image_array
        # Simple threshold-based body detection
        body_mask = (gray > 50) & (gray < 220)
    
    return body_mask

def find_body_centerline(body_mask, height):
    """Find the centerline of the body at each height level"""
    centerline = []
    
    for y in range(height):
        row = body_mask[y, :]
        body_pixels = np.where(row)[0]
        
        if len(body_pixels) > 0:
            # Find center of body mass at this height
            center_x = int(np.mean(body_pixels))
        else:
            # Use previous centerline point if available
            center_x = centerline[-1] if centerline else body_mask.shape[1] // 2
        
        centerline.append(center_x)
    
    # Smooth the centerline to remove noise
    centerline = smooth_centerline(centerline)
    
    return centerline

def smooth_centerline(centerline):
    """Smooth the centerline using a moving average"""
    smoothed = []
    window_size = 5
    
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

def estimate_shoulder_width(body_mask, shoulder_y):
    """Estimate shoulder width at the shoulder line"""
    if shoulder_y >= body_mask.shape[0]:
        return body_mask.shape[1] // 4
    
    row = body_mask[shoulder_y, :]
    body_pixels = np.where(row)[0]
    
    if len(body_pixels) > 0:
        return int(np.max(body_pixels) - np.min(body_pixels))
    else:
        return body_mask.shape[1] // 4

def estimate_hip_width(body_mask, hip_y):
    """Estimate hip width at the hip line"""
    if hip_y >= body_mask.shape[0]:
        return body_mask.shape[1] // 5
    
    row = body_mask[hip_y, :]
    body_pixels = np.where(row)[0]
    
    if len(body_pixels) > 0:
        return int((np.max(body_pixels) - np.min(body_pixels)) * 0.8)  # Hips narrower than shoulders
    else:
        return body_mask.shape[1] // 5

def estimate_knee_width(body_mask, knee_y):
    """Estimate knee width at the knee line"""
    if knee_y >= body_mask.shape[0]:
        return body_mask.shape[1] // 8
    
    row = body_mask[knee_y, :]
    body_pixels = np.where(row)[0]
    
    if len(body_pixels) > 0:
        return int((np.max(body_pixels) - np.min(body_pixels)) * 0.6)  # Knees narrower than hips
    else:
        return body_mask.shape[1] // 8

def estimate_ankle_width(body_mask, ankle_y):
    """Estimate ankle width at the ankle line"""
    if ankle_y >= body_mask.shape[0]:
        return body_mask.shape[1] // 10
    
    row = body_mask[ankle_y, :]
    body_pixels = np.where(row)[0]
    
    if len(body_pixels) > 0:
        return int((np.max(body_pixels) - np.min(body_pixels)) * 0.4)  # Ankles narrower than knees
    else:
        return body_mask.shape[1] // 10

def create_proportional_landmarks(image_array, width, height):
    """Create anatomically proportional landmarks as fallback"""
    # Use standard anatomical proportions
    center_x = width // 2
    
    # Adjust center based on image content
    if len(image_array.shape) == 3:
        gray = np.mean(image_array, axis=2)
        # Find the most likely body center by looking for vertical consistency
        vertical_profile = np.mean(gray[height//4:3*height//4, :], axis=0)
        # Find the peak in the middle region (likely torso)
        middle_region = vertical_profile[width//4:3*width//4]
        if len(middle_region) > 0:
            peak_idx = np.argmax(middle_region) + width//4
            center_x = peak_idx
    
    return {
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

def binary_erosion(image, kernel):
    """Simple binary erosion without scipy"""
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
    """Simple binary dilation without scipy"""
    result = np.zeros_like(image, dtype=bool)
    kh, kw = kernel.shape
    padded = np.pad(image, ((kh//2, kh//2), (kw//2, kw//2)), mode='constant')
    
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded[i:i+kh, j:j+kw]
            if np.any(region[kernel == 1]):
                result[i, j] = True
    return result
    """Find the main body outline in the image"""
    # Simple edge detection to find body contours
    # This is a simplified version - in reality, this would use more sophisticated methods
    edges = np.gradient(gray)
    edge_strength = np.sqrt(edges[0]**2 + edges[1]**2)
    
    # Find areas with strong edges (likely body outline)
    threshold = np.percentile(edge_strength, 85)  # Top 15% of edge strength
    body_outline = edge_strength > threshold
    
    return np.any(body_outline)  # Return True if body detected

def find_centerline_x(gray, y, width):
    """Find the centerline of the body at a given y coordinate"""
    if y >= gray.shape[0]:
        return width // 2
    
    row = gray[y, :]
    
    # Find edges in the row
    gradient = np.gradient(row)
    edge_strength = np.abs(gradient)
    
    # Find the two strongest edges (likely body sides)
    if len(edge_strength) > 10:
        # Smooth the signal
        smoothed = np.convolve(edge_strength, np.ones(5)/5, mode='same')
        
        # Find peaks
        peaks = []
        for i in range(5, len(smoothed)-5):
            if smoothed[i] > smoothed[i-1] and smoothed[i] > smoothed[i+1]:
                if smoothed[i] > np.percentile(smoothed, 75):  # Only significant peaks
                    peaks.append(i)
        
        if len(peaks) >= 2:
            # Take the two most prominent peaks
            peak_strengths = [(i, smoothed[i]) for i in peaks]
            peak_strengths.sort(key=lambda x: x[1], reverse=True)
            
            left_edge = min(peak_strengths[0][0], peak_strengths[1][0])
            right_edge = max(peak_strengths[0][0], peak_strengths[1][0])
            
            return (left_edge + right_edge) // 2
    
    return width // 2

def find_shoulder_points(gray, y, width):
    """Find left and right shoulder points"""
    center_x = find_centerline_x(gray, y, width)
    
    # Estimate shoulder width (typically 2-2.5 head widths)
    head_width = width * 0.12  # Approximate head width
    shoulder_width = head_width * 2.2
    
    left_shoulder = (int(center_x - shoulder_width//2), y)
    right_shoulder = (int(center_x + shoulder_width//2), y)
    
    return left_shoulder, right_shoulder

def find_hip_points(gray, y, width):
    """Find left and right hip points"""
    center_x = find_centerline_x(gray, y, width)
    
    # Hip width is typically slightly narrower than shoulders
    hip_width = width * 0.15
    
    left_hip = (int(center_x - hip_width//2), y)
    right_hip = (int(center_x + hip_width//2), y)
    
    return left_hip, right_hip

def find_knee_points(gray, y, width):
    """Find left and right knee points"""
    center_x = find_centerline_x(gray, y, width)
    
    # Knee width is typically narrower than hips
    knee_width = width * 0.08
    
    left_knee = (int(center_x - knee_width//2), y)
    right_knee = (int(center_x + knee_width//2), y)
    
    return left_knee, right_knee

def find_ankle_points(gray, y, width):
    """Find left and right ankle points"""
    center_x = find_centerline_x(gray, y, width)
    
    # Ankle width
    ankle_width = width * 0.06
    
    left_ankle = (int(center_x - ankle_width//2), y)
    right_ankle = (int(center_x + ankle_width//2), y)
    
    return left_ankle, right_ankle

def create_annotated_image(image_array, landmarks, analysis):
    """Create image with clinical measurement dots and lines"""
    # Convert numpy array to PIL Image
    if image_array.dtype != np.uint8:
        image_array = (image_array * 255).astype(np.uint8)
    
    pil_image = Image.fromarray(image_array)
    draw = ImageDraw.Draw(pil_image)
    
    # Color coding for clinical assessment
    colors = {
        'excellent': '#00FF00',    # Green
        'good': '#90EE90',         # Light Green  
        'fair': '#FFD700',         # Yellow
        'poor': '#FFA500',         # Orange
        'very_poor': '#FF0000'     # Red
    }
    
    # Dot size based on image size
    dot_size = max(8, min(20, image_array.shape[1] // 80))
    line_width = max(2, dot_size // 4)
    
    # Draw clinical reference lines
    # Vertical alignment line (from skull to ankle center)
    skull_pos = landmarks.get('skull', (0, 0))
    ankle_center = ((landmarks['left_ankle'][0] + landmarks['right_ankle'][0])//2, 
                    (landmarks['left_ankle'][1] + landmarks['right_ankle'][1])//2)
    
    draw.line([skull_pos, ankle_center], fill='#FFFFFF', width=2)
    
    # Horizontal reference lines for symmetry
    shoulder_y = landmarks['shoulder_center'][1]
    hip_y = landmarks['hip_center'][1]
    
    draw.line([(0, shoulder_y), (image_array.shape[1], shoulder_y)], fill='#CCCCCC', width=1)
    draw.line([(0, hip_y), (image_array.shape[1], hip_y)], fill='#CCCCCC', width=1)
    
    # Determine colors based on analysis scores
    def get_score_color(score):
        if score >= 4:
            return colors['excellent']
        elif score >= 3:
            return colors['good']
        elif score >= 2:
            return colors['fair']
        else:
            return colors['poor']
    
    # Draw landmarks with color coding
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
            
            # Draw outer circle (white border)
            draw.ellipse([
                pos[0] - dot_size - 2, pos[1] - dot_size - 2,
                pos[0] + dot_size + 2, pos[1] + dot_size + 2
            ], fill='#FFFFFF')
            
            # Draw inner circle (color coded)
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
    
    # Draw symmetry comparison lines
    # Shoulder symmetry
    draw.line([landmarks['left_shoulder'], landmarks['right_shoulder']], 
             fill=get_score_color(analysis.get('shoulder_score', 2)), width=line_width)
    
    # Hip symmetry  
    draw.line([landmarks['left_hip'], landmarks['right_hip']], 
             fill=get_score_color(analysis.get('hip_score', 2)), width=line_width)
    
    return pil_image

def advanced_cv_analysis_with_landmarks(image_array):
    """Advanced computer vision posture analysis with landmark detection"""
    height, width = image_array.shape[:2]
    
    # Estimate anatomical landmarks
    landmarks = estimate_anatomical_landmarks(image_array)
    
    # Calculate clinical measurements
    measurements = calculate_clinical_measurements(landmarks, width, height)
    
    # Convert to grayscale for symmetry analysis
    if len(image_array.shape) == 3:
        gray = np.mean(image_array, axis=2).astype(np.uint8)
    else:
        gray = image_array
    
    # Bilateral symmetry analysis
    left_half = gray[:, :width//2]
    right_half = np.fliplr(gray[:, width//2:])
    
    min_width = min(left_half.shape[1], right_half.shape[1])
    left_half = left_half[:, :min_width]
    right_half = right_half[:, :min_width]
    
    if left_half.shape == right_half.shape:
        diff = np.abs(left_half.astype(float) - right_half.astype(float))
        symmetry_score = 100 - (np.mean(diff) / 255 * 100)
    else:
        symmetry_score = 50
    
    # Calculate scores based on measurements
    head_score = calculate_head_score(measurements['head_alignment'])
    shoulder_score = calculate_shoulder_score(measurements['shoulder_symmetry'])
    hip_score = calculate_hip_score(measurements['hip_symmetry'])
    alignment_score = calculate_alignment_score(measurements['vertical_alignment'])
    
    # Total score
    total_score = head_score + shoulder_score + hip_score + alignment_score
    overall_percentage = (total_score / 16) * 100  # Max score is 16 (4x4)
    
    # Generate analysis results
    analysis = {
        'total_score': total_score,
        'max_score': 16,
        'percentage': overall_percentage,
        'head_score': head_score,
        'shoulder_score': shoulder_score,
        'hip_score': hip_score,
        'alignment_score': alignment_score,
        'landmarks': landmarks,
        'measurements': measurements,
        'raw_symmetry': symmetry_score
    }
    
    # Add detailed assessments
    analysis.update(generate_detailed_assessments_with_measurements(analysis))
    
    return analysis

def calculate_clinical_measurements(landmarks, width, height):
    """Calculate clinical measurements from landmarks"""
    measurements = {}
    
    # Head alignment (forward head posture)
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
    shoulder_center_x = landmarks['shoulder_center'][0]
    hip_center_x = landmarks['hip_center'][0]
    vertical_offset = abs(shoulder_center_x - hip_center_x)
    measurements['vertical_alignment'] = (vertical_offset / width) * 100
    
    return measurements

def calculate_head_score(head_alignment_percent):
    """Calculate head position score based on forward distance"""
    if head_alignment_percent <= 2:
        return 4  # Excellent
    elif head_alignment_percent <= 4:
        return 3  # Good
    elif head_alignment_percent <= 7:
        return 2  # Fair
    else:
        return 1  # Poor

def calculate_shoulder_score(shoulder_asymmetry_percent):
    """Calculate shoulder score based on height difference"""
    if shoulder_asymmetry_percent <= 1:
        return 4  # Excellent
    elif shoulder_asymmetry_percent <= 2:
        return 3  # Good
    elif shoulder_asymmetry_percent <= 4:
        return 2  # Fair
    else:
        return 1  # Poor

def calculate_hip_score(hip_asymmetry_percent):
    """Calculate hip score based on height difference"""
    if hip_asymmetry_percent <= 1:
        return 4  # Excellent
    elif hip_asymmetry_percent <= 2:
        return 3  # Good
    elif hip_asymmetry_percent <= 3:
        return 2  # Fair
    else:
        return 1  # Poor

def calculate_alignment_score(vertical_alignment_percent):
    """Calculate overall alignment score"""
    if vertical_alignment_percent <= 3:
        return 4  # Excellent
    elif vertical_alignment_percent <= 5:
        return 3  # Good
    elif vertical_alignment_percent <= 8:
        return 2  # Fair
    else:
        return 1  # Poor

def generate_detailed_assessments_with_measurements(analysis):
    """Generate detailed assessments including clinical measurements"""
    assessments = {}
    measurements = analysis['measurements']
    
    # Head assessment with measurements
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
    
    # Shoulder assessment with measurements
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
    
    # Hip assessment with measurements
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
    
    # Overall alignment with measurements
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

def generate_exercise_recommendations(analysis):
    """Generate targeted exercise recommendations"""
    recommendations = []
    
    head_score = analysis.get('head_score', 4)
    shoulder_score = analysis.get('shoulder_score', 4)
    hip_score = analysis.get('hip_score', 4)
    alignment_score = analysis.get('alignment_score', 4)
    
    if head_score < 3:
        recommendations.extend([
            "**🎯 Head & Neck Correction Program:**",
            "• Chin tucks: 3 sets of 15 holds (5 seconds each)",
            "• Deep cervical flexor strengthening",
            "• Upper trap stretches: 3 x 30 seconds",
            "• Postural awareness training",
            "• Ergonomic workstation assessment",
            ""
        ])
    
    if shoulder_score < 3:
        recommendations.extend([
            "**💪 Shoulder Symmetry Program:**",
            "• Unilateral strengthening for weaker side",
            "• Shoulder blade squeezes: 3 sets of 15",
            "• Single-arm rows: 2 sets of 12 (weaker side)",
            "• Thoracic spine mobility exercises",
            "• Mirror therapy exercises",
            ""
        ])
    
    if hip_score < 3:
        recommendations.extend([
            "**🔥 Hip Alignment Program:**",
            "• Unilateral glute strengthening",
            "• Side-lying hip abduction: 3 sets of 15",
            "• Hip flexor stretches: 3 x 30 seconds",
            "• Pelvic leveling exercises",
            "• Single-leg balance training",
            ""
        ])
    
    if alignment_score < 3:
        recommendations.extend([
            "**⚖️ Postural Alignment Program:**",
            "• Core stabilization exercises",
            "• Wall posture training: 3 x 2 minutes",
            "• Plank progressions: 3 x 30 seconds",
            "• Postural muscle strengthening",
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

def create_clickable_image_interface(image_array):
    """Create an interactive interface for manual landmark placement"""
    height, width = image_array.shape[:2]
    
    # Convert to base64 for HTML display
    pil_image = Image.fromarray(image_array.astype(np.uint8))
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Create the interactive HTML interface
    html_interface = f"""
    <div style="position: relative; display: inline-block; border: 2px solid #0066cc; border-radius: 10px; overflow: hidden;">
        <img id="postureImage" src="data:image/png;base64,{img_base64}" 
             style="width: 100%; max-width: 600px; height: auto; display: block; cursor: crosshair;"
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
    
    <div style="margin-top: 15px; padding: 15px; background: #f0f7ff; border-radius: 10px; border: 1px solid #0066cc;">
        <h4 style="color: #0066cc; margin-top: 0;">📍 Landmark Placement Guide:</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
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
        <div style="margin-top: 10px; font-size: 12px; color: #666;">
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
    """Process manually placed landmarks and convert to our format"""
    landmarks = {}
    
    for landmark in manual_landmarks:
        landmarks[landmark['name']] = (landmark['x'], landmark['y'])
    
    # Calculate shoulder and hip centers
    if 'left_shoulder' in landmarks and 'right_shoulder' in landmarks:
        left_s = landmarks['left_shoulder']
        right_s = landmarks['right_shoulder']
        landmarks['shoulder_center'] = ((left_s[0] + right_s[0])//2, (left_s[1] + right_s[1])//2)
    
    if 'left_hip' in landmarks and 'right_hip' in landmarks:
        left_h = landmarks['left_hip']
        right_h = landmarks['right_hip']
        landmarks['hip_center'] = ((left_h[0] + right_h[0])//2, (left_h[1] + right_h[1])//2)
    
    return landmarks
    """Save analysis to session state (cloud-compatible)"""
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
        "analysis_type": "Clinical CV Analysis"
    }
    
    st.session_state.posture_analyses.append(save_data)
    return True

# Custom CSS for rectangular camera view (landscape orientation)
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

.stCamera > div > div > div > canvas {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    border-radius: 10px !important;
}

/* Make camera container rectangular */
.stCamera {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
</style>
""", unsafe_allow_html=True)

# Main App
st.title("🤖 AI Clinical Assistant")
st.markdown("### *Visual Posture Analysis with Clinical Measurement Dots*")

# System status
if MEDIAPIPE_AVAILABLE:
    st.success("✅ MediaPipe AI available - Using advanced landmark detection")
else:
    st.info("🔬 Using clinical computer vision analysis with visual measurement markers")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🎯 Clinical Analysis Settings")
    
    patient_name = st.text_input("Patient Name", value="Anonymous")
    
    analysis_mode = st.selectbox(
        "📸 Analysis Mode",
        ["Upload Image", "Take Photo (Rectangular View for Side Analysis)", "Manual Landmark Placement"]
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
    
    📏 **Clinical Measurements:**
    - Head forward position (% of width)
    - Shoulder height difference (% of height)
    - Hip level asymmetry (% of height) 
    - Vertical alignment offset (% of width)
    """)
    
    st.markdown("---")
    st.header("🔬 Analysis Features")
    st.markdown("""
    **Clinical Grade Assessment:**
    - Anatomical landmark detection
    - Bilateral symmetry analysis
    - Quantified measurements
    - Color-coded visual feedback
    - Evidence-based scoring
    """)

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📷 Clinical Posture Analysis")
    
    if analysis_mode == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload a side-view photo for clinical analysis",
            type=['jpg', 'jpeg', 'png'],
            help="Best results with side-view, full-body photos"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            # Analyze posture with landmarks
            with st.spinner("🔬 Performing clinical analysis..."):
                analysis = advanced_cv_analysis_with_landmarks(image_array)
            
            # Create annotated image with measurement dots
            annotated_image = create_annotated_image(image_array, analysis['landmarks'], analysis)
            
            # Display images side by side
            img_col1, img_col2 = st.columns(2)
            with img_col1:
                st.image(image, caption="📷 Original Photo", use_column_width=True)
            with img_col2:
                st.image(annotated_image, caption="🎯 Clinical Measurement Points", use_column_width=True)
            
            # Display results
            with col2:
                st.header("📊 Clinical Analysis")
                
                # Main score
                score = analysis['percentage']
                st.metric(
                    "Clinical Posture Score",
                    f"{analysis['total_score']}/16",
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
                
                st.metric("Clinical Risk Level", analysis['risk_level'])
                
                # Detailed clinical measurements
                with st.expander("📏 Clinical Measurements", expanded=True):
                    measurements = analysis['measurements']
                    st.write(f"{analysis['head_color']} **Head Position:** {analysis['head_assessment']}")
                    st.write(f"{analysis['shoulder_color']} **Shoulders:** {analysis['shoulder_assessment']}")
                    st.write(f"{analysis['hip_color']} **Hips:** {analysis['hip_assessment']}")
                    st.write(f"{analysis['alignment_color']} **Alignment:** {analysis['alignment_assessment']}")
                    
                    st.markdown("**📊 Raw Measurements:**")
                    st.write(f"• Head forward: {measurements['head_alignment']:.1f}% of image width")
                    st.write(f"• Shoulder asymmetry: {measurements['shoulder_symmetry']:.1f}% of image height")
                    st.write(f"• Hip asymmetry: {measurements['hip_symmetry']:.1f}% of image height")
                    st.write(f"• Vertical misalignment: {measurements['vertical_alignment']:.1f}% of image width")
                
                # Save button
                if st.button("💾 Save Clinical Analysis", use_container_width=True):
                    if save_analysis_data(analysis, patient_name):
                        st.success("✅ Clinical analysis saved!")
                        st.balloons()
            
            # Exercise recommendations
            st.subheader("💪 Clinical Exercise Prescription")
            st.markdown("*Based on quantified postural measurements*")
            
            recommendations = generate_exercise_recommendations(analysis)
            
            for rec in recommendations:
                if rec.startswith("**") and rec.endswith("**"):
                    st.markdown(rec)
                elif rec == "":
                    st.markdown("")
                else:
                    st.markdown(rec)
    
    elif analysis_mode == "Manual Landmark Placement":
        st.header("🎯 Manual Clinical Landmark Placement")
        st.info("📍 Click directly on anatomical landmarks for precise clinical measurement")
        
        uploaded_file = st.file_uploader(
            "Upload photo for manual landmark placement",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear side-view photo for precise landmark placement"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            
            # Initialize session state for manual landmarks
            if 'manual_landmarks' not in st.session_state:
                st.session_state.manual_landmarks = None
            if 'landmarks_placed' not in st.session_state:
                st.session_state.landmarks_placed = False
            
            # Display interactive interface
            st.markdown("### 📍 Click on the image to place landmarks:")
            
            # Create clickable interface
            html_interface = create_clickable_image_interface(image_array)
            st.components.v1.html(html_interface, height=700)
            
            # Manual landmark input as backup
            st.markdown("---")
            st.markdown("### 🔧 Manual Coordinate Entry (Alternative)")
            
            with st.expander("Enter landmark coordinates manually"):
                col1, col2, col3 = st.columns(3)
                
                manual_coords = {}
                landmarks_list = [
                    ('skull', 'Skull/Head'),
                    ('left_shoulder', 'Left Shoulder'),
                    ('right_shoulder', 'Right Shoulder'),
                    ('left_hip', 'Left Hip'),
                    ('right_hip', 'Right Hip'),
                    ('left_knee', 'Left Knee'),
                    ('right_knee', 'Right Knee'),
                    ('left_ankle', 'Left Ankle'),
                    ('right_ankle', 'Right Ankle')
                ]
                
                for i, (key, label) in enumerate(landmarks_list):
                    col = [col1, col2, col3][i % 3]
                    with col:
                        st.write(f"**{label}**")
                        x = st.number_input(f"X", key=f"{key}_x", min_value=0, max_value=image_array.shape[1])
                        y = st.number_input(f"Y", key=f"{key}_y", min_value=0, max_value=image_array.shape[0])
                        manual_coords[key] = (int(x), int(y))
                
                if st.button("📍 Use Manual Coordinates"):
                    st.session_state.manual_landmarks = [
                        {'name': key, 'x': coords[0], 'y': coords[1]} 
                        for key, coords in manual_coords.items()
                    ]
                    st.session_state.landmarks_placed = True
                    st.success("✅ Manual coordinates saved!")
            
            # Calculate button and results
            if st.session_state.landmarks_placed or st.session_state.manual_landmarks:
                st.markdown("---")
                
                if st.button("🔬 Calculate Clinical Analysis", use_container_width=True, type="primary"):
                    if st.session_state.manual_landmarks:
                        # Process manual landmarks
                        with st.spinner("🔬 Calculating clinical measurements from manual landmarks..."):
                            landmarks = process_manual_landmarks(st.session_state.manual_landmarks)
                            analysis = calculate_clinical_measurements_from_landmarks(landmarks, image_array.shape[1], image_array.shape[0])
                        
                        # Create annotated image
                        annotated_image = create_annotated_image(image_array, landmarks, analysis)
                        
                        # Display results
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.subheader("📊 Clinical Analysis Results")
                            
                            # Display images side by side
                            img_col1, img_col2 = st.columns(2)
                            with img_col1:
                                st.image(image, caption="📷 Original Photo", use_column_width=True)
                            with img_col2:
                                st.image(annotated_image, caption="🎯 Manual Landmark Analysis", use_column_width=True)
                        
                        with col2:
                            st.subheader("📈 Clinical Scores")
                            
                            # Main score
                            score = analysis['percentage']
                            st.metric(
                                "Clinical Posture Score",
                                f"{analysis['total_score']}/16",
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
                            
                            st.metric("Clinical Risk Level", analysis['risk_level'])
                            
                            # Detailed measurements
                            with st.expander("📏 Precise Clinical Measurements", expanded=True):
                                measurements = analysis['measurements']
                                st.write(f"{analysis['head_color']} **Head:** {analysis['head_assessment']}")
                                st.write(f"{analysis['shoulder_color']} **Shoulders:** {analysis['shoulder_assessment']}")
                                st.write(f"{analysis['hip_color']} **Hips:** {analysis['hip_assessment']}")
                                st.write(f"{analysis['alignment_color']} **Alignment:** {analysis['alignment_assessment']}")
                                
                                st.markdown("**📊 Precise Measurements:**")
                                st.write(f"• Head forward: {measurements['head_alignment']:.2f}% of image width")
                                st.write(f"• Shoulder asymmetry: {measurements['shoulder_symmetry']:.2f}% of image height")
                                st.write(f"• Hip asymmetry: {measurements['hip_symmetry']:.2f}% of image height")
                                st.write(f"• Vertical misalignment: {measurements['vertical_alignment']:.2f}% of image width")
                            
                            # Save button
                            if st.button("💾 Save Manual Analysis", use_container_width=True):
                                if save_analysis_data(analysis, patient_name):
                                    st.success("✅ Manual analysis saved!")
                                    st.balloons()
                        
                        # Exercise recommendations
                        st.subheader("💪 Clinical Exercise Prescription")
                        st.markdown("*Based on manually validated landmark measurements*")
                        
                        recommendations = generate_exercise_recommendations(analysis)
                        
                        for rec in recommendations:
                            if rec.startswith("**") and rec.endswith("**"):
                                st.markdown(rec)
                            elif rec == "":
                                st.markdown("")
                            else:
                                st.markdown(rec)
                    
                    else:
                        st.warning("⚠️ Please place all 9 landmarks before calculating.")
            
            else:
                st.info("👆 Click on the image above to place anatomical landmarks, or use the manual coordinate entry below.")

def calculate_clinical_measurements_from_landmarks(landmarks, width, height):
    """Calculate clinical measurements from manually placed landmarks"""
    measurements = {}
    
    # Head alignment (forward head posture)
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
    shoulder_center_x = landmarks['shoulder_center'][0]
    hip_center_x = landmarks['hip_center'][0]
    vertical_offset = abs(shoulder_center_x - hip_center_x)
    measurements['vertical_alignment'] = (vertical_offset / width) * 100
    
    # Calculate scores based on measurements
    head_score = calculate_head_score(measurements['head_alignment'])
    shoulder_score = calculate_shoulder_score(measurements['shoulder_symmetry'])
    hip_score = calculate_hip_score(measurements['hip_symmetry'])
    alignment_score = calculate_alignment_score(measurements['vertical_alignment'])
    
    # Total score
    total_score = head_score + shoulder_score + hip_score + alignment_score
    overall_percentage = (total_score / 16) * 100
    
    # Generate analysis results
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
    
    # Add detailed assessments
    analysis.update(generate_detailed_assessments_with_measurements(analysis))
    
    return analysis
    
    elif analysis_mode == "Take Photo (Rectangular View for Side Analysis)":
        st.info("📸 Camera optimized for side-view full-body capture")
        st.markdown("**Instructions:** Stand sideways to camera, full body visible in rectangular frame")
        
        picture = st.camera_input("Take a side-view photo for clinical analysis")
        
        if picture is not None:
            image = Image.open(picture)
            image_array = np.array(image)
            
            # Analyze posture with landmarks
            with st.spinner("🔬 Performing clinical analysis..."):
                analysis = advanced_cv_analysis_with_landmarks(image_array)
            
            # Create annotated image
            annotated_image = create_annotated_image(image_array, analysis['landmarks'], analysis)
            
            # Display annotated result
            st.image(annotated_image, caption="🎯 Your Clinical Analysis with Measurement Points", use_column_width=True)
            
            with col2:
                st.header("📊 Your Clinical Results")
                
                score = analysis['percentage']
                st.metric("Clinical Score", f"{analysis['total_score']}/16")
                st.progress(score / 100)
                
                if analysis['overall_color'] == 'success':
                    st.success(f"✅ {analysis['overall']}")
                elif analysis['overall_color'] == 'info':
                    st.info(f"ℹ️ {analysis['overall']}")
                elif analysis['overall_color'] == 'warning':
                    st.warning(f"⚠️ {analysis['overall']}")
                else:
                    st.error(f"❌ {analysis['overall']}")
                
                # Quick clinical summary
                with st.expander("📏 Your Measurements", expanded=True):
                    measurements = analysis['measurements']
                    st.write(f"**Head:** {measurements['head_alignment']:.1f}% forward")
                    st.write(f"**Shoulders:** {measurements['shoulder_symmetry']:.1f}% asymmetry")
                    st.write(f"**Hips:** {measurements['hip_symmetry']:.1f}% asymmetry")
                    st.write(f"**Alignment:** {measurements['vertical_alignment']:.1f}% offset")
                
                if st.button("💾 Save Analysis"):
                    if save_analysis_data(analysis, patient_name):
                        st.success("✅ Saved!")
            
            # Show personalized recommendations
            st.subheader("💡 Your Clinical Exercise Plan")
            recommendations = generate_exercise_recommendations(analysis)
            for rec in recommendations:
                if rec.startswith("**") and rec.endswith("**"):
                    st.markdown(rec)
                elif rec == "":
                    st.markdown("")
                else:
                    st.markdown(rec)

# Progress tracking
if 'posture_analyses' in st.session_state and len(st.session_state.posture_analyses) > 0:
    st.markdown("---")
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
<div style='text-align: center; color: #666; font-size: 14px;'>
🤖 <strong>AI Clinical Assistant</strong> • Visual posture analysis with clinical measurement validation<br>
Quantified assessment • Evidence-based scoring • Professional documentation • HIPAA-compliant
</div>
""", unsafe_allow_html=True)
