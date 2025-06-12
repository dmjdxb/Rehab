import streamlit as st
import pandas as pd
import os
import re


st.title("🔍 Advanced Exercise Search")
st.markdown("Search and filter the exercise database to find the most appropriate interventions for your patients.")

# Load exercise database
csv_path = "exercise_index_master.csv"

try:
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        st.success(f"✅ Loaded {len(df)} exercises from database")
    else:
        st.warning("⚠️ No exercise database found. Please add exercises using the 'Add New Exercise' page.")
        
        # Option to create sample database
        if st.button("🔧 Create Sample Exercise Database"):
            sample_exercises = [
                {
                    "Injury": "ACL",
                    "Phase": "Early",
                    "Exercise": "Quad Sets",
                    "Type": "Isometric",
                    "Goal": "Activate quadriceps and reduce swelling",
                    "Equipment": "None",
                    "Progression": "Hold 5s, progress to 10s, add ankle weights",
                    "Evidence": "Wilk et al. 2012 - Sports Health",
                    "VideoURL": "",
                    "DateAdded": "2024-01-01"
                },
                {
                    "Injury": "ACL",
                    "Phase": "Mid",
                    "Exercise": "Single Leg Glute Bridge",
                    "Type": "Strength",
                    "Goal": "Improve hip stability and posterior chain strength",
                    "Equipment": "None",
                    "Progression": "Bodyweight to resistance band to weighted",
                    "Evidence": "Distefano et al. 2009 - J Orthop Sports Phys Ther",
                    "VideoURL": "",
                    "DateAdded": "2024-01-01"
                },
                {
                    "Injury": "ACL",
                    "Phase": "Late",
                    "Exercise": "Single Leg Drop Landing",
                    "Type": "Plyometric",
                    "Goal": "Improve landing mechanics and neuromuscular control",
                    "Equipment": "Box or step",
                    "Progression": "20cm to 40cm height, add perturbations",
                    "Evidence": "Myer et al. 2006 - Am J Sports Med",
                    "VideoURL": "",
                    "DateAdded": "2024-01-01"
                },
                {
                    "Injury": "Hamstring",
                    "Phase": "Early",
                    "Exercise": "Prone Knee Flexion",
                    "Type": "Mobility",
                    "Goal": "Gentle hamstring activation without overstretching",
                    "Equipment": "None",
                    "Progression": "Passive to active assisted to active",
                    "Evidence": "Heiderscheit et al. 2010 - J Orthop Sports Phys Ther",
                    "VideoURL": "",
                    "DateAdded": "2024-01-01"
                },
                {
                    "Injury": "Achilles",
                    "Phase": "Mid",
                    "Exercise": "Eccentric Heel Drops",
                    "Type": "Strength",
                    "Goal": "Promote tendon remodeling and strength",
                    "Equipment": "Step or platform",
                    "Progression": "Bodyweight to weighted, bilateral to unilateral",
                    "Evidence": "Alfredson et al. 1998 - Knee Surg Sports Traumatol Arthrosc",
                    "VideoURL": "",
                    "DateAdded": "2024-01-01"
                },
                {
                    "Injury": "Rotator Cuff",
                    "Phase": "Early",
                    "Exercise": "Pendulum Swings",
                    "Type": "Mobility",
                    "Goal": "Gentle passive range of motion",
                    "Equipment": "Light weight (1-2 lbs)",
                    "Progression": "No weight to light weight, increase range",
                    "Evidence": "Kuhn et al. 2009 - J Bone Joint Surg Am",
                    "VideoURL": "",
                    "DateAdded": "2024-01-01"
                }
            ]
            
            sample_df = pd.DataFrame(sample_exercises)
            sample_df.to_csv(csv_path, index=False)
            st.success("✅ Sample exercise database created! Please refresh the page.")
            st.stop()
        
        st.stop()
        
except Exception as e:
    st.error(f"Error loading exercise database: {e}")
    st.stop()

# Database statistics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Exercises", len(df))
with col2:
    st.metric("Injury Types", df['Injury'].nunique())
with col3:
    st.metric("Exercise Types", df['Type'].nunique())
with col4:
    st.metric("Phases Covered", df['Phase'].nunique())

st.markdown("---")

# Search and filter interface
search_col, filter_col = st.columns([2, 1])

with search_col:
    st.subheader("🔎 Search Exercises")
    
    # Text search
    search_term = st.text_input(
        "Search in exercise name, goal, or evidence:",
        placeholder="e.g., 'glute bridge', 'eccentric', 'landing'",
        help="Search across exercise names, goals, and evidence sources"
    )
    
    # Advanced search options
    with st.expander("🔧 Advanced Search Options"):
        search_fields = st.multiselect(
            "Search in specific fields:",
            options=['Exercise', 'Goal', 'Evidence', 'Progression', 'Equipment'],
            default=['Exercise', 'Goal']
        )
        
        case_sensitive = st.checkbox("Case sensitive search")
        whole_word = st.checkbox("Whole word only")

with filter_col:
    st.subheader("📂 Filters")
    
    # Get unique values for filters
    injuries = ['All'] + sorted(df['Injury'].dropna().unique().tolist())
    phases = ['All'] + sorted(df['Phase'].dropna().unique().tolist())
    types = ['All'] + sorted(df['Type'].dropna().unique().tolist())
    
    # Filter controls
    selected_injury = st.selectbox("Injury Type", injuries)
    selected_phase = st.selectbox("Rehab Phase", phases)
    selected_type = st.selectbox("Exercise Type", types)
    
    # Equipment filter
    equipment_options = ['All', 'None (Bodyweight)'] + [eq for eq in df['Equipment'].dropna().unique() if eq.lower() not in ['none', '']]
    selected_equipment = st.selectbox("Equipment", equipment_options)
    
    # Evidence-based filter
    has_evidence = st.checkbox("Show only evidence-based exercises")

# Apply filters
filtered_df = df.copy()

# Apply category filters
if selected_injury != 'All':
    filtered_df = filtered_df[filtered_df['Injury'] == selected_injury]

if selected_phase != 'All':
    filtered_df = filtered_df[filtered_df['Phase'] == selected_phase]

if selected_type != 'All':
    filtered_df = filtered_df[filtered_df['Type'] == selected_type]

if selected_equipment != 'All':
    if selected_equipment == 'None (Bodyweight)':
        filtered_df = filtered_df[filtered_df['Equipment'].str.lower().isin(['none', '', 'bodyweight'])]
    else:
        filtered_df = filtered_df[filtered_df['Equipment'].str.contains(selected_equipment, case=False, na=False)]

# Evidence filter
if has_evidence:
    filtered_df = filtered_df[filtered_df['Evidence'].notna() & (filtered_df['Evidence'].str.strip() != '')]

# Apply text search
if search_term:
    search_term_processed = search_term if case_sensitive else search_term.lower()
    
    def search_in_fields(row):
        for field in search_fields:
            if field in row.index and pd.notna(row[field]):
                field_text = str(row[field]) if case_sensitive else str(row[field]).lower()
                
                if whole_word:
                    # Use word boundaries for whole word search
                    pattern = r'\b' + re.escape(search_term_processed) + r'\b'
                    if re.search(pattern, field_text):
                        return True
                else:
                    if search_term_processed in field_text:
                        return True
        return False
    
    filtered_df = filtered_df[filtered_df.apply(search_in_fields, axis=1)]

# Display results
st.markdown("---")
st.subheader(f"📋 Search Results ({len(filtered_df)} exercises found)")

if len(filtered_df) == 0:
    st.warning("No exercises match your search criteria. Try adjusting your filters.")
else:
    # Sort options
    sort_col1, sort_col2 = st.columns([3, 1])
    
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by:",
            options=['Exercise', 'Injury', 'Phase', 'Type', 'DateAdded'],
            index=0
        )
    
    with sort_col2:
        sort_order = st.selectbox("Order:", ['Ascending', 'Descending'])
    
    # Apply sorting
    ascending = sort_order == 'Ascending'
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(sort_by, ascending=ascending)
    
    # Display options
    display_options = st.multiselect(
        "Select columns to display:",
        options=['Exercise', 'Injury', 'Phase', 'Type', 'Goal', 'Equipment', 'Progression', 'Evidence', 'VideoURL'],
        default=['Exercise', 'Injury', 'Phase', 'Type', 'Goal', 'Equipment']
    )
    
    if display_options:
        # Create display dataframe
        display_df = filtered_df[display_options].copy()
        
        # Format for better display
        if 'VideoURL' in display_options:
            display_df['VideoURL'] = display_df['VideoURL'].apply(
                lambda x: '🎥 Video' if pd.notna(x) and x.strip() != '' else ''
            )
        
        # Make the dataframe interactive
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                'Exercise': st.column_config.TextColumn('Exercise', width='medium'),
                'Goal': st.column_config.TextColumn('Goal', width='large'),
                'VideoURL': st.column_config.TextColumn('Video', width='small')
            }
        )
        
        # Exercise details expander
        if len(filtered_df) <= 10:  # Only show details for small result sets
            with st.expander("📖 View Exercise Details"):
                for idx, row in filtered_df.iterrows():
                    with st.container():
                        st.markdown(f"### {row['Exercise']}")
                        
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            st.markdown(f"**Injury:** {row['Injury']}")
                            st.markdown(f"**Phase:** {row['Phase']}")
                            st.markdown(f"**Type:** {row['Type']}")
                            st.markdown(f"**Equipment:** {row['Equipment']}")
                        
                        with detail_col2:
                            st.markdown(f"**Goal:** {row['Goal']}")
                            if pd.notna(row['Evidence']) and row['Evidence'].strip():
                                st.markdown(f"**Evidence:** {row['Evidence']}")
                            if pd.notna(row['VideoURL']) and row['VideoURL'].strip():
                                st.markdown(f"**Video:** [Watch on YouTube]({row['VideoURL']})")
                        
                        if pd.notna(row['Progression']) and row['Progression'].strip():
                            st.markdown(f"**Progression:** {row['Progression']}")
                        
                        st.markdown("---")
    
    # Export options
    st.subheader("📁 Export Results")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📊 Export to CSV", use_container_width=True):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV File",
                data=csv,
                file_name=f"exercise_search_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with export_col2:
        if st.button("📋 Copy Search URL", use_container_width=True):
            # Create a summary of current filters for sharing
            filter_summary = []
            if selected_injury != 'All':
                filter_summary.append(f"Injury: {selected_injury}")
            if selected_phase != 'All':
                filter_summary.append(f"Phase: {selected_phase}")
            if selected_type != 'All':
                filter_summary.append(f"Type: {selected_type}")
            if search_term:
                filter_summary.append(f"Search: '{search_term}'")
            
            summary_text = "Current search: " + ", ".join(filter_summary) if filter_summary else "All exercises"
            st.code(summary_text)

# Quick filters (preset combinations)
st.markdown("---")
st.subheader("⚡ Quick Filters")

quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

with quick_col1:
    if st.button("🏃‍♂️ Return to Sport", use_container_width=True):
        st.rerun()

with quick_col2:
    if st.button("💪 Strength Only", use_container_width=True):
        st.rerun()

with quick_col3:
    if st.button("🏠 Home Exercises", use_container_width=True):
        st.rerun()

with quick_col4:
    if st.button("📚 Evidence-Based", use_container_width=True):
        st.rerun()
