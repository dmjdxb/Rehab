# patient_session_manager.py
# This module handles patient session management across all pages

import streamlit as st
import pandas as pd
import os
from datetime import datetime

PATIENT_DB_PATH = "patient_database.csv"
SESSION_LOG_PATH = "session_log.csv"

class PatientSessionManager:
    """Manages patient selection and data across all pages"""
    
    @staticmethod
    def init_session_state():
        """Initialize session state variables for patient management"""
        if 'current_patient_id' not in st.session_state:
            st.session_state.current_patient_id = None
        if 'current_patient_name' not in st.session_state:
            st.session_state.current_patient_name = None
        if 'current_patient_data' not in st.session_state:
            st.session_state.current_patient_data = None
    
    @staticmethod
    def load_patient_database():
        """Load patient database"""
        if os.path.exists(PATIENT_DB_PATH):
            return pd.read_csv(PATIENT_DB_PATH)
        return pd.DataFrame()
    
    @staticmethod
    def get_current_patient():
        """Get currently selected patient data"""
        PatientSessionManager.init_session_state()
        return st.session_state.current_patient_data
    
    @staticmethod
    def set_current_patient(patient_id):
        """Set the current patient by ID"""
        patient_df = PatientSessionManager.load_patient_database()
        
        if len(patient_df) > 0 and patient_id in patient_df['PatientID'].values:
            patient = patient_df[patient_df['PatientID'] == patient_id].iloc[0]
            st.session_state.current_patient_id = patient_id
            st.session_state.current_patient_name = f"{patient['FirstName']} {patient['LastName']}"
            st.session_state.current_patient_data = patient.to_dict()
            return True
        return False
    
    @staticmethod
    def clear_current_patient():
        """Clear the current patient selection"""
        st.session_state.current_patient_id = None
        st.session_state.current_patient_name = None
        st.session_state.current_patient_data = None
    
    @staticmethod
    def create_patient_selector(key="patient_selector", show_info=True):
        """Create a patient selector widget that can be used on any page"""
        PatientSessionManager.init_session_state()
        patient_df = PatientSessionManager.load_patient_database()
        
        if len(patient_df) == 0:
            st.warning("No patients registered. Please add patients in the Patient Management page.")
            if st.button("Go to Patient Management"):
                st.switch_page("pages/patient_management.py")
            return None
        
        # Create patient list for selection
        patient_options = ["Select a patient..."] + [
            f"{p['FirstName']} {p['LastName']} ({p['PatientID']})" 
            for _, p in patient_df.iterrows()
        ]
        
        # Get current selection index
        current_index = 0
        if st.session_state.current_patient_id:
            for i, option in enumerate(patient_options):
                if st.session_state.current_patient_id in option:
                    current_index = i
                    break
        
        # Patient selector
        selected = st.selectbox(
            "🔍 Select Patient",
            patient_options,
            index=current_index,
            key=key
        )
        
        if selected != "Select a patient...":
            # Extract patient ID from selection
            patient_id = selected.split('(')[-1].strip(')')
            PatientSessionManager.set_current_patient(patient_id)
            
            if show_info and st.session_state.current_patient_data:
                # Show patient info card
                patient = st.session_state.current_patient_data
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                    
                    with col1:
                        st.metric("Patient", st.session_state.current_patient_name)
                    
                    with col2:
                        age = PatientSessionManager.calculate_age(patient['DateOfBirth'])
                        st.metric("Age/Sex", f"{age}y / {patient['Sex'][0]}")
                    
                    with col3:
                        st.metric("Injury", patient['InjuryType'])
                    
                    with col4:
                        st.metric("Phase", patient['CurrentPhase'])
                
                st.markdown("---")
            
            return patient_id
        
        return None
    
    @staticmethod
    def calculate_age(dob_str):
        """Calculate age from date of birth"""
        try:
            dob = pd.to_datetime(dob_str)
            today = datetime.now()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            return 0
    
    @staticmethod
    def get_patient_sessions(patient_name=None):
        """Get all sessions for current patient or specified patient"""
        if patient_name is None:
            patient_name = st.session_state.get('current_patient_name')
        
        if not patient_name or not os.path.exists(SESSION_LOG_PATH):
            return pd.DataFrame()
        
        session_df = pd.read_csv(SESSION_LOG_PATH)
        return session_df[session_df['Athlete'] == patient_name]
    
    @staticmethod
    def add_session_entry(session_data):
        """Add a new session entry for the current patient"""
        if not st.session_state.current_patient_name:
            return False
        
        # Ensure patient name is in session data
        session_data['Athlete'] = st.session_state.current_patient_name
        
        # Load existing sessions or create new dataframe
        if os.path.exists(SESSION_LOG_PATH):
            session_df = pd.read_csv(SESSION_LOG_PATH)
        else:
            session_df = pd.DataFrame()
        
        # Add new session
        new_session_df = pd.DataFrame([session_data])
        session_df = pd.concat([session_df, new_session_df], ignore_index=True)
        
        # Save
        session_df.to_csv(SESSION_LOG_PATH, index=False)
        return True
    
    @staticmethod
    def update_patient_phase(patient_id, new_phase):
        """Update patient's current rehab phase"""
        patient_df = PatientSessionManager.load_patient_database()
        
        if patient_id in patient_df['PatientID'].values:
            patient_df.loc[patient_df['PatientID'] == patient_id, 'CurrentPhase'] = new_phase
            patient_df.loc[patient_df['PatientID'] == patient_id, 'LastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            patient_df.to_csv(PATIENT_DB_PATH, index=False)
            
            # Update session state if this is the current patient
            if st.session_state.current_patient_id == patient_id:
                st.session_state.current_patient_data['CurrentPhase'] = new_phase
            
            return True
        return False


# Example usage functions for different pages

def rehab_engine_integration():
    """Example of how to integrate in rehab_engine.py"""
    st.title("🏃‍♂️ Rehab Engine")
    
    # Patient selector at the top
    patient_id = PatientSessionManager.create_patient_selector()
    
    if patient_id:
        patient = PatientSessionManager.get_current_patient()
        
        # Your existing rehab engine code here
        # But now it uses the selected patient's data
        
        # When saving a session:
        session_data = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": datetime.now().strftime("%H:%M"),
            "Athlete": st.session_state.current_patient_name,  # Automatically filled
            "Injury": patient['InjuryType'],  # From patient data
            "Phase": patient['CurrentPhase'],  # From patient data
            "Peak Force": 1000,  # Your measurements
            "Left Limb": 480,
            "Right Limb": 520,
            "Symmetry Index": 92.3,
            "RFD": 78.5,
            "Pain Score": 2,
            "Notes": "Session notes here"
        }
        
        if st.button("Save Session"):
            if PatientSessionManager.add_session_entry(session_data):
                st.success("Session saved successfully!")


def patient_dashboard_integration():
    """Example of how to integrate in patient_dashboard.py"""
    st.title("📊 Patient Dashboard")
    
    # Patient selector
    patient_id = PatientSessionManager.create_patient_selector()
    
    if patient_id:
        # Get patient's sessions
        sessions = PatientSessionManager.get_patient_sessions()
        
        if len(sessions) > 0:
            # Your existing dashboard visualizations
            # But now automatically filtered for selected patient
            st.success(f"Showing {len(sessions)} sessions for {st.session_state.current_patient_name}")
        else:
            st.info("No sessions recorded yet for this patient.")


def clinical_assessments_integration():
    """Example of how to integrate in clinical_assessments.py"""
    st.title("📊 Clinical Assessments")
    
    # Patient selector
    patient_id = PatientSessionManager.create_patient_selector()
    
    if patient_id:
        patient = PatientSessionManager.get_current_patient()
        
        # Your assessment forms here
        # Pre-populate with patient data where relevant
        
        # When saving assessment:
        assessment_data = {
            "patient_id": patient_id,
            "patient_name": st.session_state.current_patient_name,
            "assessment_type": "IKDC",
            "score": 85,
            "date": datetime.now().strftime("%Y-%m-%d"),
            # ... other assessment data
        }
        
        # You could save this to a separate assessments file
        # or include it in the session log


def exercise_prescription_integration():
    """Example of how to integrate in exercise pages"""
    patient_id = PatientSessionManager.create_patient_selector(show_info=False)
    
    if patient_id:
        patient = PatientSessionManager.get_current_patient()
        
        # Filter exercises based on patient's injury and phase
        injury_type = patient['InjuryType']
        current_phase = patient['CurrentPhase']
        
        st.info(f"Showing exercises for {injury_type} - {current_phase} phase")
        
        # Your exercise filtering code here