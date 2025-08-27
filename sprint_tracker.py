import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# Page config
st.set_page_config(
    page_title="Sprint Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean styling
st.markdown("""
<style>
    .status-in-progress { background-color: #e3f2fd; color: #1565c0; padding: 4px 8px; border-radius: 4px; }
    .status-on-hold { background-color: #fff3e0; color: #ef6c00; padding: 4px 8px; border-radius: 4px; }
    .status-completed { background-color: #e8f5e8; color: #2e7d32; padding: 4px 8px; border-radius: 4px; }
    .status-planned { background-color: #f3e5f5; color: #7b1fa2; padding: 4px 8px; border-radius: 4px; }
    .metric-box { background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# Google Sheets configuration
# Replace the init_google_sheets function in your sprint_tracker.py with this:

@st.cache_resource
# Replace your init_google_sheets function with this version:
def init_google_sheets():
    """Initialize Google Sheets connection"""
    try:
        # Get credentials from Streamlit secrets
        if "gcp_service_account" in st.secrets:
            credentials_info = st.secrets["gcp_service_account"]
            credentials = Credentials.from_service_account_info(
                credentials_info,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
        else:
            st.error("Google Cloud credentials not found in Streamlit secrets.")
            return None
        
        gc = gspread.authorize(credentials)
        
        # Try to open existing spreadsheet or create new one
        spreadsheet_name = "Sprint Tracker Data"
        try:
            spreadsheet = gc.open(spreadsheet_name)
            st.success(f"✅ Connected to existing spreadsheet")
        except gspread.SpreadsheetNotFound:
            # Create new spreadsheet in service account's drive
            spreadsheet = gc.create(spreadsheet_name)
            st.success(f"✅ Created new spreadsheet in service account drive")
            
            # Share with your personal Google account so you can access it
            try:
                # Replace this with YOUR email address (the one you use for Google Drive)
                your_email = "andremikhailserra3@gmail.com"  # ← Change this to your email
                spreadsheet.share(your_email, perm_type='user', role='writer')
                st.info(f"📧 Shared spreadsheet with {your_email}")
            except Exception as share_error:
                st.warning(f"Created spreadsheet but couldn't share: {share_error}")
                st.info("You can manually access it via the service account or share it yourself")
            
            # Initialize sheets with headers and sample data
            init_sheets_structure(spreadsheet)
        
        # Show the spreadsheet URL for easy access
        if hasattr(spreadsheet, 'url'):
            st.sidebar.success("✅ Connected to Google Sheets")
            if st.sidebar.button("📊 Open Spreadsheet"):
                st.sidebar.markdown(f"[View in Google Sheets]({spreadsheet.url})")
        
        return spreadsheet
    
    except Exception as e:
        error_msg = str(e)
        if "storageQuotaExceeded" in error_msg:
            st.error("❌ Google Drive storage is full!")
            st.info("💡 Solutions:")
            st.info("1. Free up space in your Google Drive")
            st.info("2. Or use a different Google account")
            st.info("3. Or let the app create the sheet in service account drive (update code)")
        else:
            st.error(f"Could not connect to Google Sheets: {error_msg}")
        return None
def init_sheets_structure(spreadsheet):
    """Initialize the Google Sheets with proper structure"""
    # Project Overview sheet
    try:
        project_sheet = spreadsheet.worksheet("Project Overview")
    except gspread.WorksheetNotFound:
        project_sheet = spreadsheet.add_worksheet(title="Project Overview", rows=100, cols=8)
    
    project_headers = ["Project", "Goal", "Start Date", "Target End Date", "Current Status", "Owner(s)", "Notes", "Created At"]
    project_sheet.update('A1:H1', [project_headers])
    
    # Daily Updates sheet
    try:
        daily_sheet = spreadsheet.worksheet("Daily Updates")
    except gspread.WorksheetNotFound:
        daily_sheet = spreadsheet.add_worksheet(title="Daily Updates", rows=500, cols=8)
    
    daily_headers = ["Date", "Project", "Developer", "Yesterday's Progress", "Today's Focus", "Blockers", "Next Milestone", "Created At"]
    daily_sheet.update('A1:H1', [daily_headers])
    
    # Sprint Goals sheet  
    try:
        sprint_sheet = spreadsheet.worksheet("Sprint Goals")
    except gspread.WorksheetNotFound:
        sprint_sheet = spreadsheet.add_worksheet(title="Sprint Goals", rows=100, cols=8)
    
    sprint_headers = ["Sprint", "Dates", "Project", "Goal", "Success Criteria", "Owner(s)", "Status", "Created At"]
    sprint_sheet.update('A1:H1', [sprint_headers])
    
    # Results & Retrospective sheet
    try:
        retro_sheet = spreadsheet.worksheet("Results & Retrospective")
    except gspread.WorksheetNotFound:
        retro_sheet = spreadsheet.add_worksheet(title="Results & Retrospective", rows=100, cols=5)
    
    retro_headers = ["Sprint", "What Went Well", "What Could Be Better", "Key Results", "Created At"]
    retro_sheet.update('A1:E1', [retro_headers])
    
    # Add sample data
    add_sample_data(spreadsheet)

def add_sample_data(spreadsheet):
    """Add sample data to sheets"""
    # Sample projects
    project_sheet = spreadsheet.worksheet("Project Overview")
    sample_projects = [
        ["Beehiiv + TinyEmail Automation", "Automate daily campaign stats to Sheets", "Aug 28", "Sept 6", "In Progress", "Andre, Partner", "Roadmap drafted, API research ongoing", datetime.now().isoformat()],
        ["Slack AI Assistant", "AI chatbot with doc parsing", "Sept 7", "Sept 15", "On Hold", "Andre", "Waiting for client feedback", datetime.now().isoformat()]
    ]
    project_sheet.update('A2:H3', sample_projects)
    
    # Sample daily updates
    daily_sheet = spreadsheet.worksheet("Daily Updates")
    sample_updates = [
        ["2025-08-27", "Beehiiv + TinyEmail", "Andre", "Finished roadmap & doc", "Start API auth setup", "Need API keys from client", "API connector working", datetime.now().isoformat()],
        ["2025-08-27", "Beehiiv + TinyEmail", "Partner", "Explored TinyEmail docs", "Build Beehiiv client prototype", "None", "End-to-end test for 1 brand", datetime.now().isoformat()],
        ["2025-08-28", "Slack AI Assistant", "Andre", "Setup Flask skeleton", "Write Slackbot listener", "None", "Slackbot responds to `/ask`", datetime.now().isoformat()]
    ]
    daily_sheet.update('A2:H4', sample_updates)
    
    # Sample sprint goals
    sprint_sheet = spreadsheet.worksheet("Sprint Goals")
    sample_sprints = [
        ["Sprint 1", "Aug 27–Sept 6", "Beehiiv + TinyEmail", "Automated ingestion & write to Sheets", "Job runs daily at 8am PH time with alerts", "Andre, Partner", "In Progress", datetime.now().isoformat()],
        ["Sprint 2", "Sept 7–Sept 15", "Slack AI Assistant", "Slackbot answers questions from uploaded docs", "Answers accurate within ±10%", "Andre", "Planned", datetime.now().isoformat()]
    ]
    sprint_sheet.update('A2:H3', sample_sprints)
    
    # Sample retrospective
    retro_sheet = spreadsheet.worksheet("Results & Retrospective")
    sample_retro = [
        ["Sprint 1", "Clear roadmap, strong API division", "Client was slow with credentials", "Automation working daily", datetime.now().isoformat()]
    ]
    retro_sheet.update('A2:E2', sample_retro)

def load_sheet_data(spreadsheet, sheet_name):
    """Load data from a specific sheet"""
    if not spreadsheet:
        return []
    
    try:
        sheet = spreadsheet.worksheet(sheet_name)
        data = sheet.get_all_records()
        return data
    except Exception as e:
        st.error(f"Error loading {sheet_name}: {str(e)}")
        return []

def append_to_sheet(spreadsheet, sheet_name, data):
    """Append a row of data to a sheet"""
    if not spreadsheet:
        st.error("Google Sheets not connected. Data not saved.")
        return False
    
    try:
        sheet = spreadsheet.worksheet(sheet_name)
        # Add timestamp
        data.append(datetime.now().isoformat())
        sheet.append_row(data)
        return True
    except Exception as e:
        st.error(f"Error saving to {sheet_name}: {str(e)}")
        return False

def get_status_badge(status):
    status_class = status.lower().replace(' ', '-')
    return f'<span class="status-{status_class}">{status}</span>'

# Initialize Google Sheets
spreadsheet = init_google_sheets()

# Sidebar navigation
st.sidebar.title("Sprint Tracker")

# Show connection status
if spreadsheet:
    st.sidebar.success("✅ Connected to Google Sheets")
    if st.sidebar.button("View Spreadsheet"):
        st.sidebar.write(f"[Open in Google Sheets]({spreadsheet.url})")
else:
    st.sidebar.error("❌ Google Sheets not connected")
    st.sidebar.info("Running in demo mode")

page = st.sidebar.selectbox(
    "Navigate to:",
    ["Project Overview", "Daily Updates", "Sprint Goals", "Results & Retrospective"]
)

if st.sidebar.button("Refresh Data"):
    st.cache_resource.clear()
    st.rerun()

# Main content
if page == "Project Overview":
    st.title("Project Overview")
    st.caption("High-level status of all projects")
    
    # Add new project
    st.subheader("Add New Project")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Project")
        goal = st.text_input("Goal")
        start_date = st.text_input("Start Date", placeholder="e.g., Aug 28")
        target_end = st.text_input("Target End Date", placeholder="e.g., Sept 6")
    
    with col2:
        status = st.selectbox("Current Status", ["In Progress", "On Hold", "Completed", "Planned"])
        owners = st.text_input("Owner(s)", placeholder="e.g., Andre, Partner")
        notes = st.text_area("Notes")
    
    if st.button("Add Project", type="primary"):
        if project_name and goal:
            data_row = [project_name, goal, start_date, target_end, status, owners, notes]
            if append_to_sheet(spreadsheet, "Project Overview", data_row):
                st.success("Project added successfully!")
                st.rerun()
        else:
            st.error("Please fill in Project and Goal fields")
    
    st.divider()
    
    # Display projects
    st.subheader("Current Projects")
    
    projects_data = load_sheet_data(spreadsheet, "Project Overview")
    
    if projects_data:
        # Display as a table with custom formatting
        for project in projects_data:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1.5, 2])
            
            with col1:
                st.write(f"**{project['Project']}**")
            with col2:
                st.write(project['Goal'])
            with col3:
                st.write(project['Start Date'])
            with col4:
                st.write(project['Target End Date'])
            with col5:
                st.markdown(get_status_badge(project['Current Status']), unsafe_allow_html=True)
            with col6:
                st.write(project['Owner(s)'])
            
            if project['Notes']:
                st.caption(f"Notes: {project['Notes']}")
            st.divider()
    else:
        st.info("No projects added yet. Add your first project above.")

elif page == "Daily Updates":
    st.title("Daily Updates")
    st.caption("Running log of daily progress (append-only)")
    
    # Add new daily update
    st.subheader("Add Daily Update")
    
    col1, col2 = st.columns(2)
    
    with col1:
        update_date = st.date_input("Date", datetime.now()).strftime('%Y-%m-%d')
        # Get project list from Google Sheets
        projects_data = load_sheet_data(spreadsheet, "Project Overview")
        project_list = [p['Project'] for p in projects_data] if projects_data else ['Beehiiv + TinyEmail', 'Slack AI Assistant']
        selected_project = st.selectbox("Project", project_list)
        developer = st.text_input("Developer", placeholder="e.g., Andre")
    
    with col2:
        yesterday_progress = st.text_area("Yesterday's Progress")
        today_focus = st.text_area("Today's Focus")
    
    col1, col2 = st.columns(2)
    with col1:
        blockers = st.text_area("Blockers", placeholder="None or describe blockers")
    with col2:
        next_milestone = st.text_area("Next Milestone")
    
    if st.button("Add Update", type="primary"):
        if selected_project and developer:
            data_row = [update_date, selected_project, developer, yesterday_progress, today_focus, blockers, next_milestone]
            if append_to_sheet(spreadsheet, "Daily Updates", data_row):
                st.success("Daily update added successfully!")
                st.rerun()
        else:
            st.error("Please fill in Project and Developer fields")
    
    st.divider()
    
    # Display daily updates
    st.subheader("Recent Updates")
    
    updates_data = load_sheet_data(spreadsheet, "Daily Updates")
    
    if updates_data:
        # Sort by date descending (most recent first)
        updates_data = sorted(updates_data, key=lambda x: x['Date'], reverse=True)
        
        for update in updates_data[:20]:  # Show last 20 updates
            with st.expander(f"{update['Date']} - {update['Project']} - {update['Developer']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Yesterday's Progress:**")
                    st.write(update["Yesterday's Progress"])
                    st.write("**Blockers:**")
                    if update['Blockers'] and update['Blockers'].lower() != 'none':
                        st.error(update['Blockers'])
                    else:
                        st.success("None")
                
                with col2:
                    st.write("**Today's Focus:**")
                    st.write(update["Today's Focus"])
                    st.write("**Next Milestone:**")
                    st.info(update['Next Milestone'])
    else:
        st.info("No daily updates yet. Add your first update above.")

elif page == "Sprint Goals":
    st.title("Sprint Goals")
    st.caption("Bi-weekly or weekly sprint objectives")
    
    # Add new sprint goal
    st.subheader("Add Sprint Goal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sprint_name = st.text_input("Sprint", placeholder="e.g., Sprint 1")
        dates = st.text_input("Dates", placeholder="e.g., Aug 27–Sept 6")
        # Get project list from Google Sheets
        projects_data = load_sheet_data(spreadsheet, "Project Overview")
        project_list = [p['Project'] for p in projects_data] if projects_data else ['Beehiiv + TinyEmail', 'Slack AI Assistant']
        sprint_project = st.selectbox("Project", project_list, key="sprint_project")
    
    with col2:
        goal = st.text_area("Goal")
        success_criteria = st.text_area("Success Criteria")
        owners = st.text_input("Owner(s)", placeholder="e.g., Andre, Partner", key="sprint_owners")
        status = st.selectbox("Status", ["In Progress", "Planned", "Completed", "On Hold"], key="sprint_status")
    
    if st.button("Add Sprint Goal", type="primary"):
        if sprint_name and sprint_project and goal:
            data_row = [sprint_name, dates, sprint_project, goal, success_criteria, owners, status]
            if append_to_sheet(spreadsheet, "Sprint Goals", data_row):
                st.success("Sprint goal added successfully!")
                st.rerun()
        else:
            st.error("Please fill in Sprint, Project, and Goal fields")
    
    st.divider()
    
    # Display sprint goals
    st.subheader("Current Sprint Goals")
    
    goals_data = load_sheet_data(spreadsheet, "Sprint Goals")
    
    if goals_data:
        for goal in goals_data:
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([1, 1.5, 1.5, 2, 1.5, 1])
                
                with col1:
                    st.write(f"**{goal['Sprint']}**")
                with col2:
                    st.write(goal['Dates'])
                with col3:
                    st.write(goal['Project'])
                with col4:
                    st.write(goal['Goal'])
                with col5:
                    st.write(goal['Success Criteria'])
                with col6:
                    st.write(goal['Owner(s)'])
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(get_status_badge(goal['Status']), unsafe_allow_html=True)
                
                st.divider()
    else:
        st.info("No sprint goals yet. Add your first sprint goal above.")

elif page == "Results & Retrospective":
    st.title("Results & Retrospective")
    st.caption("Sprint outcomes and lessons learned")
    
    # Add new retrospective
    st.subheader("Add Retrospective")
    
    sprint_name = st.text_input("Sprint", placeholder="e.g., Sprint 1")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        what_went_well = st.text_area("What Went Well")
    
    with col2:
        what_could_be_better = st.text_area("What Could Be Better")
    
    with col3:
        key_results = st.text_area("Key Results")
    
    if st.button("Add Retrospective", type="primary"):
        if sprint_name:
            data_row = [sprint_name, what_went_well, what_could_be_better, key_results]
            if append_to_sheet(spreadsheet, "Results & Retrospective", data_row):
                st.success("Retrospective added successfully!")
                st.rerun()
        else:
            st.error("Please fill in Sprint field")
    
    st.divider()
    
    # Display retrospectives
    st.subheader("Sprint Retrospectives")
    
    retro_data = load_sheet_data(spreadsheet, "Results & Retrospective")
    
    if retro_data:
        for retro in retro_data:
            st.subheader(f"Sprint: {retro['Sprint']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**What Went Well**")
                st.success(retro['What Went Well'] if retro['What Went Well'] else 'TBD')
            
            with col2:
                st.write("**What Could Be Better**")
                st.warning(retro['What Could Be Better'] if retro['What Could Be Better'] else 'TBD')
            
            with col3:
                st.write("**Key Results**")
                st.info(retro['Key Results'] if retro['Key Results'] else 'TBD')
            
            st.divider()
    else:
        st.info("No retrospectives yet. Add your first retrospective above.")

# Footer
st.divider()
st.markdown("**Sprint Tracker** - Data stored in Google Sheets")

# Display spreadsheet URL in sidebar if connected
if spreadsheet and st.sidebar.button("📊 Open Google Sheets"):
    st.sidebar.markdown(f"[View Data in Google Sheets]({spreadsheet.url})")

# Setup instructions in sidebar
with st.sidebar.expander("⚙️ Setup Instructions"):
    st.markdown("""
    **To connect Google Sheets:**
    
    1. Create Google Cloud Project
    2. Enable Google Sheets API
    3. Create Service Account
    4. Download JSON key
    5. Add to Streamlit Secrets
    
    **Streamlit Secrets format:**
    ```toml
    [gcp_service_account]
    type = "service_account"
    project_id = "your-project"
    private_key_id = "key-id"
    private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
    client_email = "your-service@project.iam.gserviceaccount.com"
    client_id = "client-id"
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    ```
    """)