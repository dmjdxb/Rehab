# 🏥 Rehabilitation Programming Toolkit

A comprehensive Streamlit-based web application designed for clinicians to manage patient rehabilitation programs, track progress, and access evidence-based exercise databases.

## 🚀 Features

- **Rehab Phase Engine**: Automatically determine rehabilitation phases based on clinical metrics
- **Exercise Database**: Searchable library of evidence-based rehabilitation exercises
- **Patient Dashboard**: Track patient progress with detailed analytics and visualizations
- **Session Logging**: Record and monitor patient sessions over time
- **Advanced Search**: Filter exercises by injury type, phase, equipment, and more

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🛠️ Installation

1. **Clone or download the project files** to your desired directory

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify file structure**:
   ```
   your-project-folder/
   ├── home.py
   ├── rehab_engine.py
   ├── requirements.txt
   ├── exercise_index_master.csv
   ├── session_log.csv
   ├── .streamlit/
   │   └── config.toml
   └── pages/
       ├── add_new_exercise.py
       ├── rehab_engine.py
       ├── patient_dashboard.py
       └── advanced_search.py
   ```

## 🏃‍♂️ Running the Application

1. **Navigate to your project directory**:
   ```bash
   cd path/to/your/rehab-toolkit
   ```

2. **Start the Streamlit app**:
   ```bash
   streamlit run home.py
   ```

3. **Open your browser** to `http://localhost:8501`

## 📊 Initial Setup

### First Time Users

1. The app includes sample data to get you started
2. Navigate through the sidebar to explore different features
3. Add your own exercises using the "Add New Exercise" page
4. Log patient sessions using the "Rehab Engine" 
5. View progress in the "Patient Dashboard"

### Data Files

- **exercise_index_master.csv**: Exercise database (grows as you add exercises)
- **session_log.csv**: Patient session data (created when you log sessions)

## 🎯 User Guide

### Home Page
- Overview of toolkit features
- Quick statistics about your database
- Navigation guidance

### Rehab Engine
- Input clinical metrics (LSI, RFD, pain scores)
- Get evidence-based phase recommendations
- Log sessions for progress tracking
- Receive clinical alerts and warnings

### Patient Dashboard
- Filter sessions by patient, date range, or injury type
- View progress charts and trend analysis
- Export data for reports
- Clinical alerts for concerning metrics

### Advanced Search
- Search exercises by keywords
- Filter by injury type, phase, equipment needs
- View detailed exercise descriptions
- Export search results

### Add New Exercise
- Contribute to the shared exercise database
- Include evidence sources and video links
- Validate entries before submission

## 🔧 Customization

### Adding New Injury Types
Edit the injury options in:
- `pages/add_new_exercise.py` (line ~45)
- `pages/rehab_engine.py` (line ~25)
- `rehab_engine.py` (add thresholds)

### Modifying Phase Thresholds
Update evidence-based thresholds in `rehab_engine.py` in the `injury_thresholds` dictionary.

### Styling
Modify `.streamlit/config.toml` to change colors and themes.

## 📚 Clinical Evidence Base

The rehabilitation phases and exercise recommendations are based on peer-reviewed research including:

- Wilk et al. (2012) - ACL rehabilitation protocols
- Alfredson et al. (1998) - Achilles tendon eccentric training
- Heiderscheit et al. (2010) - Hamstring injury management
- Myer et al. (2006) - Landing mechanics and injury prevention

## 🔒 Data Security

- All data is stored locally in CSV files
- No cloud synchronization (can be added if needed)
- Patient data remains on your local system
- Suitable for clinical environments with privacy requirements

## 🐛 Troubleshooting

### Common Issues

1. **Import Error**: Ensure all packages from `requirements.txt` are installed
2. **File Not Found**: Check that CSV files are in the correct location
3. **Page Not Loading**: Verify file structure and naming conventions
4. **Charts Not Displaying**: Ensure plotly is installed correctly

### Getting Help

- Check the Streamlit documentation: https://docs.streamlit.io
- Review error messages in the terminal
- Ensure Python version compatibility

## 🔄 Updates and Maintenance

### Regular Maintenance
- Backup your CSV files regularly
- Monitor database growth and performance
- Update exercise database with new evidence

### Version Control
Consider using Git to track changes to your exercise database and customizations.

## 📈 Future Enhancements

Potential additions:
- Cloud database integration (Firebase/PostgreSQL)
- User authentication and role management
- Advanced analytics and machine learning
- Integration with VALD testing systems
- Mobile app companion
- Automated report generation

## 📞 Support

For technical issues or feature requests, review the code comments and Streamlit documentation. The application is designed to be self-contained and customizable for different clinical environments.

---

**Built for clinicians, by understanding clinical workflows.** 
🏥 Secure • 📊 Evidence-based • 🚀 User-friendly