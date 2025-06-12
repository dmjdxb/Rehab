import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
import json

# Initialize patient database
PATIENT_DB_PATH = "patient_database.csv"
SESSION_LOG_PATH = "session_log.csv"

def load_patient_database():
    """Load patient database or create if it doesn't exist"""
    if os.path.exists(PATIENT_DB_PATH):
        return pd.read_csv(PATIENT_DB_PATH)
    else:
        # Create empty database with required columns
        columns = [
            'PatientID', 'FirstName', 'LastName', 'DateOfBirth', 'Sex', 
            'Height_cm', 'Weight_kg', 'Email', 'Phone', 'EmergencyContact',
            'InjuryType', 'InjuryDate', 'SurgeryDate', 'Surgeon', 
            'CurrentPhase', 'Goals', 'MedicalHistory', 'Medications',
            'RegistrationDate', 'LastUpdated', 'Status'
        ]
        return pd.DataFrame(columns=columns)

def save_patient_database(df):
    """Save patient database to CSV"""
    df.to_csv(PATIENT_DB_PATH, index=False)

def generate_patient_id():
    """Generate unique patient ID"""
    return f"PT{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Page title and setup
st.title("👥 Patient Management System")
st.markdown("Register new patients and manage existing patient profiles")

# Load patient database
patient_df = load_patient_database()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Register New Patient", 
    "📋 Patient Directory", 
    "👤 Patient Profile",
    "📊 Population Analytics"
])

# Tab 1: Register New Patient
with tab1:
    st.header("🆕 New Patient Registration")
    
    with st.form("patient_registration_form"):
        st.subheader("📝 Basic Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            first_name = st.text_input("First Name*", placeholder="John")
            last_name = st.text_input("Last Name*", placeholder="Doe")
            dob = st.date_input("Date of Birth*", 
                              min_value=datetime(1920, 1, 1),
                              max_value=datetime.now())
        
        with col2:
            sex = st.selectbox("Sex*", ["Male", "Female", "Other"])
            height = st.number_input("Height (cm)*", min_value=50, max_value=250, value=170)
            weight = st.number_input("Weight (kg)*", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
        
        with col3:
            email = st.text_input("Email", placeholder="john.doe@email.com")
            phone = st.text_input("Phone", placeholder="+1234567890")
            emergency_contact = st.text_input("Emergency Contact", placeholder="Name: Phone")
        
        st.subheader("🏥 Injury Information")
        col1, col2 = st.columns(2)
        
        with col1:
            injury_type = st.selectbox("Primary Injury*", [
                "ACL", "Meniscus", "Ankle Sprain", "Rotator Cuff", 
                "Tennis Elbow", "Lower Back Pain", "Patellofemoral Pain",
                "Achilles Tendinopathy", "Hip Impingement", "Other"
            ])
            
            if injury_type == "Other":
                injury_type = st.text_input("Specify Injury Type*")
            
            injury_date = st.date_input("Injury Date*", 
                                      max_value=datetime.now())
            
            had_surgery = st.checkbox("Surgical Intervention")
            
            if had_surgery:
                surgery_date = st.date_input("Surgery Date", 
                                           min_value=injury_date,
                                           max_value=datetime.now())
                surgeon = st.text_input("Surgeon Name")
            else:
                surgery_date = None
                surgeon = None
        
        with col2:
            current_phase = st.selectbox("Current Rehab Phase*", [
                "Pre-Op", "Acute (0-2 weeks)", "Early (2-6 weeks)",
                "Mid (6-12 weeks)", "Late (3-6 months)", 
                "Return to Sport (6+ months)", "Maintenance"
            ])
            
            goals = st.text_area("Patient Goals", 
                               placeholder="e.g., Return to basketball, pain-free daily activities")
        
        st.subheader("📋 Medical History")
        col1, col2 = st.columns(2)
        
        with col1:
            medical_history = st.text_area("Relevant Medical History",
                                         placeholder="Previous injuries, chronic conditions, etc.")
        
        with col2:
            medications = st.text_area("Current Medications",
                                     placeholder="List all current medications")
        
        # Submit button
        submitted = st.form_submit_button("✅ Register Patient", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not all([first_name, last_name, injury_type]):
                st.error("Please fill in all required fields marked with *")
            else:
                # Create new patient record
                new_patient = {
                    'PatientID': generate_patient_id(),
                    'FirstName': first_name,
                    'LastName': last_name,
                    'DateOfBirth': dob.strftime('%Y-%m-%d'),
                    'Sex': sex,
                    'Height_cm': height,
                    'Weight_kg': weight,
                    'Email': email,
                    'Phone': phone,
                    'EmergencyContact': emergency_contact,
                    'InjuryType': injury_type,
                    'InjuryDate': injury_date.strftime('%Y-%m-%d'),
                    'SurgeryDate': surgery_date.strftime('%Y-%m-%d') if surgery_date else None,
                    'Surgeon': surgeon,
                    'CurrentPhase': current_phase,
                    'Goals': goals,
                    'MedicalHistory': medical_history,
                    'Medications': medications,
                    'RegistrationDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'LastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Status': 'Active'
                }
                
                # Add to database
                patient_df = pd.concat([patient_df, pd.DataFrame([new_patient])], ignore_index=True)
                save_patient_database(patient_df)
                
                st.success(f"✅ Patient registered successfully! ID: {new_patient['PatientID']}")
                st.info(f"Patient: {first_name} {last_name} has been added to the system.")
                
                # Clear form by rerunning
                st.rerun()

# Tab 2: Patient Directory
with tab2:
    st.header("📋 Patient Directory")
    
    if len(patient_df) == 0:
        st.warning("No patients registered yet. Use the 'Register New Patient' tab to add patients.")
    else:
        # Search and filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Search patients", placeholder="Name or ID")
        
        with col2:
            injury_filter = st.selectbox("Filter by Injury", 
                                       ["All"] + sorted(patient_df['InjuryType'].dropna().unique().tolist()))
        
        with col3:
            status_filter = st.selectbox("Filter by Status", 
                                       ["All", "Active", "Discharged", "On Hold"])
        
        # Apply filters
        filtered_patients = patient_df.copy()
        
        if search_term:
            mask = (
                filtered_patients['FirstName'].str.contains(search_term, case=False, na=False) |
                filtered_patients['LastName'].str.contains(search_term, case=False, na=False) |
                filtered_patients['PatientID'].str.contains(search_term, case=False, na=False)
            )
            filtered_patients = filtered_patients[mask]
        
        if injury_filter != "All":
            filtered_patients = filtered_patients[filtered_patients['InjuryType'] == injury_filter]
        
        if status_filter != "All":
            filtered_patients = filtered_patients[filtered_patients['Status'] == status_filter]
        
        # Display patient cards
        st.subheader(f"Found {len(filtered_patients)} patients")
        
        for idx, patient in filtered_patients.iterrows():
            with st.expander(f"{patient['FirstName']} {patient['LastName']} - {patient['PatientID']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Age:** {calculate_age(patient['DateOfBirth'])} years")
                    st.write(f"**Sex:** {patient['Sex']}")
                    st.write(f"**Height:** {patient['Height_cm']} cm")
                    st.write(f"**Weight:** {patient['Weight_kg']} kg")
                    st.write(f"**BMI:** {calculate_bmi(patient['Weight_kg'], patient['Height_cm'])}")
                
                with col2:
                    st.write(f"**Injury:** {patient['InjuryType']}")
                    st.write(f"**Injury Date:** {patient['InjuryDate']}")
                    st.write(f"**Current Phase:** {patient['CurrentPhase']}")
                    st.write(f"**Status:** {patient['Status']}")
                
                with col3:
                    st.write(f"**Email:** {patient['Email']}")
                    st.write(f"**Phone:** {patient['Phone']}")
                    st.write(f"**Registered:** {patient['RegistrationDate']}")
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                with btn_col1:
                    if st.button(f"👤 View Profile", key=f"view_{patient['PatientID']}"):
                        st.session_state['selected_patient_id'] = patient['PatientID']
                        st.session_state['active_tab'] = 2  # Switch to profile tab
                        st.rerun()
                
                with btn_col2:
                    if st.button(f"📊 View Progress", key=f"progress_{patient['PatientID']}"):
                        st.session_state['dashboard_patient'] = f"{patient['FirstName']} {patient['LastName']}"
                        st.switch_page("pages/patient_dashboard.py")
                
                with btn_col3:
                    if st.button(f"🏃 Start Session", key=f"session_{patient['PatientID']}"):
                        st.session_state['session_patient'] = f"{patient['FirstName']} {patient['LastName']}"
                        st.switch_page("pages/rehab_engine.py")

# Tab 3: Patient Profile
with tab3:
    st.header("👤 Patient Profile")
    
    if len(patient_df) == 0:
        st.warning("No patients registered yet.")
    else:
        # Patient selection
        patient_names = [f"{p['FirstName']} {p['LastName']} ({p['PatientID']})" 
                        for _, p in patient_df.iterrows()]
        
        selected_patient_name = st.selectbox("Select Patient", patient_names)
        
        if selected_patient_name:
            # Extract patient ID from selection
            patient_id = selected_patient_name.split('(')[-1].strip(')')
            patient = patient_df[patient_df['PatientID'] == patient_id].iloc[0]
            
            # Display patient information
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Patient avatar placeholder
                st.markdown(
                    f"""
                    <div style="
                        width: 150px;
                        height: 150px;
                        background-color: #f0f0f0;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 48px;
                        font-weight: bold;
                        color: #666;
                        margin: 20px auto;
                    ">
                        {patient['FirstName'][0]}{patient['LastName'][0]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.metric("Patient ID", patient['PatientID'])
                st.metric("Status", patient['Status'])
            
            with col2:
                st.subheader(f"{patient['FirstName']} {patient['LastName']}")
                
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.write(f"**Age:** {calculate_age(patient['DateOfBirth'])} years")
                    st.write(f"**DOB:** {patient['DateOfBirth']}")
                    st.write(f"**Sex:** {patient['Sex']}")
                    st.write(f"**BMI:** {calculate_bmi(patient['Weight_kg'], patient['Height_cm'])}")
                
                with info_col2:
                    st.write(f"**Height:** {patient['Height_cm']} cm")
                    st.write(f"**Weight:** {patient['Weight_kg']} kg")
                    st.write(f"**Email:** {patient['Email']}")
                    st.write(f"**Phone:** {patient['Phone']}")
            
            # Tabs for different sections
            profile_tab1, profile_tab2, profile_tab3, profile_tab4 = st.tabs([
                "🏥 Clinical Info", "📊 Progress Summary", "📝 Session Notes", "✏️ Edit Profile"
            ])
            
            with profile_tab1:
                st.subheader("Clinical Information")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Primary Injury:**", patient['InjuryType'])
                    st.write("**Injury Date:**", patient['InjuryDate'])
                    st.write("**Days Since Injury:**", calculate_days_since(patient['InjuryDate']))
                    st.write("**Current Phase:**", patient['CurrentPhase'])
                    
                    if pd.notna(patient['SurgeryDate']):
                        st.write("**Surgery Date:**", patient['SurgeryDate'])
                        st.write("**Surgeon:**", patient['Surgeon'])
                        st.write("**Days Post-Op:**", calculate_days_since(patient['SurgeryDate']))
                
                with col2:
                    st.write("**Patient Goals:**")
                    st.info(patient['Goals'] if pd.notna(patient['Goals']) else "No goals specified")
                    
                    st.write("**Medical History:**")
                    st.info(patient['MedicalHistory'] if pd.notna(patient['MedicalHistory']) else "No history recorded")
                    
                    st.write("**Current Medications:**")
                    st.info(patient['Medications'] if pd.notna(patient['Medications']) else "No medications listed")
            
            with profile_tab2:
                st.subheader("Progress Summary")
                
                # Load session data for this patient
                full_name = f"{patient['FirstName']} {patient['LastName']}"
                
                if os.path.exists(SESSION_LOG_PATH):
                    session_df = pd.read_csv(SESSION_LOG_PATH)
                    patient_sessions = session_df[session_df['Athlete'] == full_name]
                    
                    if len(patient_sessions) > 0:
                        # Summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Sessions", len(patient_sessions))
                        
                        with col2:
                            latest_lsi = patient_sessions.iloc[-1]['Symmetry Index']
                            st.metric("Latest LSI", f"{latest_lsi:.1f}%")
                        
                        with col3:
                            latest_pain = patient_sessions.iloc[-1]['Pain Score']
                            st.metric("Latest Pain", f"{latest_pain}/10")
                        
                        with col4:
                            days_in_rehab = calculate_days_since(patient['InjuryDate'])
                            st.metric("Days in Rehab", days_in_rehab)
                        
                        # Progress chart
                        if len(patient_sessions) >= 2:
                            patient_sessions['Date'] = pd.to_datetime(patient_sessions['Date'])
                            
                            fig = go.Figure()
                            
                            # Add LSI line
                            fig.add_trace(go.Scatter(
                                x=patient_sessions['Date'],
                                y=patient_sessions['Symmetry Index'],
                                mode='lines+markers',
                                name='LSI (%)',
                                line=dict(color='blue', width=2),
                                yaxis='y'
                            ))
                            
                            # Add Pain line
                            fig.add_trace(go.Scatter(
                                x=patient_sessions['Date'],
                                y=patient_sessions['Pain Score'] * 10,  # Scale to match LSI
                                mode='lines+markers',
                                name='Pain (scaled)',
                                line=dict(color='red', width=2, dash='dot'),
                                yaxis='y'
                            ))
                            
                            # Add target line
                            fig.add_hline(y=90, line_dash="dash", line_color="green",
                                        annotation_text="LSI Target")
                            
                            fig.update_layout(
                                title="Progress Overview",
                                xaxis_title="Date",
                                yaxis_title="Score (%)",
                                hovermode='x unified',
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No sessions recorded yet for this patient.")
                else:
                    st.info("No session data available.")
            
            with profile_tab3:
                st.subheader("Session Notes")
                
                # Add new note
                with st.form("add_note"):
                    note_type = st.selectbox("Note Type", 
                                           ["Progress Note", "Clinical Observation", "Patient Feedback", "Other"])
                    note_text = st.text_area("Note Content")
                    
                    if st.form_submit_button("Add Note"):
                        # Here you would save the note to a database
                        st.success("Note added successfully!")
                
                # Display existing notes (placeholder)
                st.info("Session notes will appear here once implemented with database integration.")
            
            with profile_tab4:
                st.subheader("Edit Patient Profile")
                
                with st.form("edit_patient"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_weight = st.number_input("Update Weight (kg)", 
                                                   value=float(patient['Weight_kg']), 
                                                   step=0.5)
                        new_phase = st.selectbox("Update Phase", 
                                               ["Pre-Op", "Acute (0-2 weeks)", "Early (2-6 weeks)",
                                                "Mid (6-12 weeks)", "Late (3-6 months)", 
                                                "Return to Sport (6+ months)", "Maintenance"],
                                               index=["Pre-Op", "Acute (0-2 weeks)", "Early (2-6 weeks)",
                                                     "Mid (6-12 weeks)", "Late (3-6 months)", 
                                                     "Return to Sport (6+ months)", "Maintenance"]
                                               .index(patient['CurrentPhase']))
                        new_status = st.selectbox("Update Status",
                                                ["Active", "Discharged", "On Hold"],
                                                index=["Active", "Discharged", "On Hold"]
                                                .index(patient['Status']))
                    
                    with col2:
                        new_goals = st.text_area("Update Goals", value=patient['Goals'])
                        new_meds = st.text_area("Update Medications", value=patient['Medications'])
                    
                    if st.form_submit_button("Save Changes"):
                        # Update patient record
                        patient_df.loc[patient_df['PatientID'] == patient_id, 'Weight_kg'] = new_weight
                        patient_df.loc[patient_df['PatientID'] == patient_id, 'CurrentPhase'] = new_phase
                        patient_df.loc[patient_df['PatientID'] == patient_id, 'Status'] = new_status
                        patient_df.loc[patient_df['PatientID'] == patient_id, 'Goals'] = new_goals
                        patient_df.loc[patient_df['PatientID'] == patient_id, 'Medications'] = new_meds
                        patient_df.loc[patient_df['PatientID'] == patient_id, 'LastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        save_patient_database(patient_df)
                        st.success("✅ Patient profile updated successfully!")
                        st.rerun()

# Tab 4: Population Analytics
with tab4:
    st.header("📊 Population Analytics")
    
    if len(patient_df) == 0:
        st.warning("No patients registered yet.")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Patients", len(patient_df))
        
        with col2:
            active_patients = len(patient_df[patient_df['Status'] == 'Active'])
            st.metric("Active Patients", active_patients)
        
        with col3:
            avg_age = patient_df['DateOfBirth'].apply(calculate_age).mean()
            st.metric("Average Age", f"{avg_age:.1f} years")
        
        with col4:
            injury_types = patient_df['InjuryType'].nunique()
            st.metric("Injury Types", injury_types)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Injury distribution
            injury_counts = patient_df['InjuryType'].value_counts()
            fig_injury = px.pie(values=injury_counts.values, 
                              names=injury_counts.index,
                              title="Distribution by Injury Type")
            st.plotly_chart(fig_injury, use_container_width=True)
        
        with col2:
            # Phase distribution
            phase_counts = patient_df['CurrentPhase'].value_counts()
            fig_phase = px.bar(x=phase_counts.index, 
                             y=phase_counts.values,
                             title="Patients by Rehab Phase",
                             labels={'x': 'Phase', 'y': 'Number of Patients'})
            st.plotly_chart(fig_phase, use_container_width=True)
        
        # Age and sex distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Age distribution
            patient_df['Age'] = patient_df['DateOfBirth'].apply(calculate_age)
            fig_age = px.histogram(patient_df, x='Age', 
                                 title="Age Distribution",
                                 nbins=20)
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            # Sex distribution
            sex_counts = patient_df['Sex'].value_counts()
            fig_sex = px.pie(values=sex_counts.values,
                           names=sex_counts.index,
                           title="Distribution by Sex")
            st.plotly_chart(fig_sex, use_container_width=True)

# Helper functions
def calculate_age(dob_str):
    """Calculate age from date of birth string"""
    try:
        dob = pd.to_datetime(dob_str)
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except:
        return 0

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI"""
    try:
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return f"{bmi:.1f}"
    except:
        return "N/A"

def calculate_days_since(date_str):
    """Calculate days since a given date"""
    try:
        date = pd.to_datetime(date_str)
        days = (datetime.now() - date).days
        return days
    except:
        return 0

# Add custom CSS for better styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)
