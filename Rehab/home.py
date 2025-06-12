import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Rehab Toolkit Home",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Main title and description
st.title("🏥 Rehab Programming Toolkit")
st.markdown("""
Welcome to the **Clinician Rehab Dashboard**, designed for daily use in clinical and performance settings.

This tool integrates:
- ✅ VALD and clinical metric tracking
- ✅ Adaptive rehab phase guidance
- ✅ Evidence-based exercise selection
- ✅ Historical progress monitoring
- ✅ Clinician-controlled content management

---

### 🚀 Navigate using the sidebar to:
- **Patient Dashboard** - Access patient progress and session history
- **Rehab Engine** - Calculate rehab progression based on clinical metrics
- **Advanced Search** - Search and filter exercise database
- **Add New Exercise** - Contribute new evidence-based exercises

---

### 📊 Quick Stats
""")

# Display quick stats about the system
try:
    # Check if exercise database exists
    csv_path = "exercise_index_master.csv"
    if os.path.exists(csv_path):
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Exercises", len(df))
        with col2:
            st.metric("Injury Types", df['Injury'].nunique())
        with col3:
            st.metric("Exercise Types", df['Type'].nunique())
    else:
        st.info("📝 Exercise database will be created when you add your first exercise.")
        
    # Check if session log exists
    session_path = "session_log.csv"
    if os.path.exists(session_path):
        df_sessions = pd.read_csv(session_path)
        st.metric("Total Sessions Logged", len(df_sessions))
    else:
        st.info("📈 Patient session data will appear here once you start logging sessions.")
        
except Exception as e:
    st.warning("⚠️ Some data files may need to be initialized. This is normal for first-time setup.")

st.markdown("""
---

### 💡 Getting Started

1. **First time?** Start by adding exercises using the "Add New Exercise" page
2. **Have patient data?** Use the "Rehab Engine" to determine appropriate phases
3. **Need exercises?** Search the database using "Advanced Search"
4. **Track progress?** Log sessions and view trends in "Patient Dashboard"

---

### 🔧 Technical Notes

- All data is stored locally in CSV files
- Exercise database grows as clinicians contribute
- Patient data remains private and secure
- Compatible with VALD testing systems

---

Need help or want to contribute to the exercise library?
**Contact support** or submit new ideas via the "Add New Exercise" tab.

---
🔐 Secure, private, and built for real-world rehab environments.
""")

# Add a footer with system status
st.markdown("---")
st.caption("💻 System Status: Online | 📅 Last Updated: Current Session | 🔒 Data: Local Storage")
