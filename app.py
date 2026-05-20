"""
Vendor Profile Submission Portal
A Streamlit application for vendors to submit candidate profiles and admins to manage requirements
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import io
from pathlib import Path
import base64

# Configuration
DATA_DIR = Path("portal_data")
SUBMISSIONS_DIR = DATA_DIR / "submissions"
REQUIREMENTS_FILE = DATA_DIR / "requirements.json"
SUBMISSIONS_LOG = DATA_DIR / "submissions_log.csv"
UPLOADS_DIR = DATA_DIR / "uploads"
VENDORS_FILE = DATA_DIR / "vendors.json"
VENDOR_LIMITS_FILE = DATA_DIR / "vendor_limits.json"

# Create directories if they don't exist
for directory in [DATA_DIR, SUBMISSIONS_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'vendor_name' not in st.session_state:
    st.session_state.vendor_name = None

# Admin credentials (in production, use proper authentication)
ADMIN_PASSWORD = "admin123"

def load_vendors():
    """Load vendors from JSON file"""
    if VENDORS_FILE.exists():
        with open(VENDORS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_vendors(vendors):
    """Save vendors to JSON file"""
    with open(VENDORS_FILE, 'w') as f:
        json.dump(vendors, f, indent=2)

def load_requirements():
    """Load requirements from JSON file"""
    if REQUIREMENTS_FILE.exists():
        with open(REQUIREMENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_requirements(requirements):
    """Save requirements to JSON file"""
    with open(REQUIREMENTS_FILE, 'w') as f:
        json.dump(requirements, f, indent=2)

def load_submissions_log():
    """Load submissions log"""
    if SUBMISSIONS_LOG.exists():
        return pd.read_csv(SUBMISSIONS_LOG)
    return pd.DataFrame(columns=[
        'timestamp', 'vendor_name', 'req_id', 'candidate_name', 
        'resume_file', 'id_file', 'submission_sheet', 'status'
    ])

def save_submission_log(log_df):
    """Save submissions log"""
def load_vendor_limits():
    """Load vendor-specific submission limits from JSON file"""
    if VENDOR_LIMITS_FILE.exists():
        with open(VENDOR_LIMITS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_vendor_limits(limits):
    """Save vendor-specific submission limits to JSON file"""
    with open(VENDOR_LIMITS_FILE, 'w') as f:
        json.dump(limits, f, indent=2)

def get_vendor_submission_limit(vendor_name, req_id):
    """Get the submission limit for a specific vendor and requirement
    Returns custom limit if set, otherwise returns default limit of 2"""
    limits = load_vendor_limits()
    key = f"{vendor_name}|{req_id}"
    return limits.get(key, 2)  # Default is 2 submissions

def set_vendor_submission_limit(vendor_name, req_id, limit):
    """Set a custom submission limit for a specific vendor and requirement"""
    limits = load_vendor_limits()
    key = f"{vendor_name}|{req_id}"
    limits[key] = limit
    save_vendor_limits(limits)

def count_vendor_submissions(vendor_name, req_id):
    """Count how many submissions a vendor has made for a specific requirement"""
    log_df = load_submissions_log()
    if log_df.empty:
        return 0
    return len(log_df[(log_df['vendor_name'] == vendor_name) & (log_df['req_id'] == req_id)])

def get_base64_image(image_path):
    """Convert image to base64 string"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return ""

def login_page():
    """Professional login page with IBM and Amex branding"""
    
    # Custom CSS for professional styling
    st.markdown("""
        <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container styling */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Header styling */
        .login-header {
            text-align: center;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        
        .main-title {
            color: #0066CC;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .subtitle {
            color: #555;
            font-size: 1.2rem;
            font-weight: 400;
        }
        
        /* Login card styling - transparent background */
        .login-card {
            background: transparent;
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
        }
        
        .card-title {
            color: #0066CC;
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            text-align: center;
            border-bottom: 3px solid #0066CC;
            padding-bottom: 0.75rem;
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 0.875rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #0066CC;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
            background: white;
        }
        
        .stTextInput > label {
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #333 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #0066CC 0%, #004999 100%);
            color: white;
            font-weight: 600;
            padding: 1rem;
            border-radius: 10px;
            border: none;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 102, 204, 0.5);
            background: linear-gradient(135deg, #0052a3 0%, #003d7a 100%);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Alert styling */
        .stAlert {
            border-radius: 10px;
            font-size: 0.95rem;
            margin-top: 1rem;
        }
        
        /* Footer styling */
        .login-footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid rgba(0, 102, 204, 0.2);
        }
        
        .footer-text {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }
        
        .footer-brands {
            color: #0066CC;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        /* Icon styling */
        .icon {
            font-size: 1.5rem;
            margin-right: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="login-header">
            <div class="main-title">🔐 Vendor Management Portal</div>
            <div class="subtitle">IBM & American Express Partnership</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout for login forms
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">👤 Vendor Login</div>', unsafe_allow_html=True)
        
        vendors = load_vendors()
        
        # Use form to enable Enter key submission
        with st.form(key="vendor_form"):
            vendor_name = st.text_input("Username", key="vendor_login", placeholder="Enter your username")
            vendor_password = st.text_input("Password", type="password", key="vendor_pass", placeholder="Enter your password")
            vendor_submit = st.form_submit_button("🔓 Login as Vendor")
            
            if vendor_submit:
                if not vendor_name or not vendor_password:
                    st.error("⚠️ Please enter both username and password")
                elif vendor_name not in vendors:
                    st.error("❌ Vendor not found. Please contact admin.")
                elif vendors[vendor_name]['password'] != vendor_password:
                    st.error("❌ Invalid password")
                elif vendors[vendor_name]['status'] != 'active':
                    st.error("❌ Your account is inactive. Please contact admin.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "vendor"
                    st.session_state.vendor_name = vendor_name
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚙️ Admin Login</div>', unsafe_allow_html=True)
        
        # Use form to enable Enter key submission
        with st.form(key="admin_form"):
            admin_password = st.text_input("Admin Password", type="password", key="admin_login", placeholder="Enter admin password")
            admin_submit = st.form_submit_button("🔓 Login as Admin")
            
            if admin_submit:
                if admin_password == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "admin"
                    st.success("✅ Admin login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid admin password")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div class="login-footer">
            <div class="footer-text">Secure Vendor Management System</div>
            <div class="footer-brands">IBM & American Express</div>
            <div class="footer-text" style="margin-top: 0.5rem;">© 2026 All Rights Reserved</div>
        </div>
    """, unsafe_allow_html=True)

def vendor_portal():
    """Vendor submission portal"""
    st.title("📤 Vendor Profile Submission Portal")
    st.write(f"Welcome, **{st.session_state.vendor_name}**!")
    
    if st.button("Logout", key="vendor_logout"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.vendor_name = None
        st.rerun()
    
    st.divider()
    
    # Initialize session state for tracking submission success
    if 'submission_success' not in st.session_state:
        st.session_state.submission_success = False
    if 'last_selected_req' not in st.session_state:
        st.session_state.last_selected_req = None
    
    # Load requirements
    requirements = load_requirements()
    
    if not requirements:
        st.warning("⚠️ No active requirements available. Please contact the administrator.")
        return
    
    # Display active requirements with total submissions count
    st.subheader("📋 Active Requirements")
    
    # Load all submissions to count total submissions per requirement
    all_submissions = load_submissions_log()
    
    req_options = []
    for req_id, req_data in requirements.items():
        if req_data.get('status') == 'active':
            # Count total submissions for this requirement (from all vendors)
            total_submissions = len(all_submissions[all_submissions['req_id'] == req_id]) if not all_submissions.empty else 0
            req_options.append(f"{req_id} - {req_data['title']} ({req_data['location']}) - Rate: ${req_data['rate']}/hr - Positions: {req_data['positions']} - Total Submissions: {total_submissions}")
    
    if not req_options:
        st.warning("⚠️ No active requirements available at this time.")
        return
    
    selected_req = st.selectbox("Select Requirement", req_options, key="req_selector")
    req_id = selected_req.split(" - ")[0]
    
    # Reset submission success flag when requirement changes
    if st.session_state.last_selected_req != req_id:
        st.session_state.submission_success = False
        st.session_state.last_selected_req = req_id
    
    # Check submission limit (custom or default)
    submission_count = count_vendor_submissions(st.session_state.vendor_name, req_id)
    submission_limit = get_vendor_submission_limit(st.session_state.vendor_name, req_id)
    remaining_slots = submission_limit - submission_count
    
    # Show submission status with prominent messaging
    if submission_limit > 2:
        # Custom limit has been granted
        st.success(f"✅ **Special Approval Granted!** Admin has increased your submission limit to **{submission_limit}** profiles for this requirement.")
    
    if remaining_slots > 0:
        st.info(f"📊 Submission Status: **{submission_count}/{submission_limit}** profiles submitted | **{remaining_slots} more slot(s) available**")
    else:
        st.info(f"📊 Submission Status: **{submission_count}/{submission_limit}** profiles submitted")
    
    if submission_count >= submission_limit:
        st.error(f"❌ You have reached the maximum limit of {submission_limit} submissions for this requirement.")
        st.info("💡 Please select a different requirement to submit another candidate, or contact admin for additional slots.")
        # Show submissions section and return
        st.divider()
        st.subheader("📊 Your Submissions")
        log_df = load_submissions_log()
        vendor_submissions = log_df[log_df['vendor_name'] == st.session_state.vendor_name]
        
        if not vendor_submissions.empty:
            display_df = vendor_submissions[['timestamp', 'req_id', 'candidate_name', 'status']].copy()
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No submissions yet")
        return
    
    st.divider()
    
    # Show submission form only if not successfully submitted
    if not st.session_state.submission_success:
        # Submission form
        st.subheader("📝 Submit Candidate Profile")
        
        with st.form("submission_form"):
            candidate_name = st.text_input("Candidate Name *", placeholder="Enter candidate full name")
            candidate_email = st.text_input("Candidate Email", placeholder="candidate@email.com")
            candidate_phone = st.text_input("Candidate Phone", placeholder="+1 (XXX) XXX-XXXX")
            
            st.write("**Upload Documents:**")
            resume_file = st.file_uploader(
                "Resume (PDF, DOC, DOCX) *",
                type=['pdf', 'doc', 'docx'],
                help="Upload candidate resume"
            )
            
            id_file = st.file_uploader(
                "Candidate ID (JPG, JPEG, PNG) *",
                type=['jpg', 'jpeg', 'png'],
                help="Upload candidate photo ID"
            )
            
            submission_sheet = st.file_uploader(
                "Submission Excel Sheet (XLSX, XLS) *",
                type=['xlsx', 'xls'],
                help="Upload completed submission form"
            )
            
            additional_notes = st.text_area("Additional Notes", placeholder="Any additional information about the candidate")
            
            submitted = st.form_submit_button("Submit Profile")
            
            if submitted:
                # Validation
                if not candidate_name:
                    st.error("❌ Candidate name is required")
                elif not resume_file:
                    st.error("❌ Resume file is required")
                elif not id_file:
                    st.error("❌ Candidate ID is required")
                elif not submission_sheet:
                    st.error("❌ Submission Excel sheet is required")
                else:
                    # Save files
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    vendor_folder = UPLOADS_DIR / st.session_state.vendor_name / req_id / timestamp
                    vendor_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Save uploaded files
                    resume_path = vendor_folder / f"resume_{resume_file.name}"
                    id_path = vendor_folder / f"id_{id_file.name}"
                    sheet_path = vendor_folder / f"submission_{submission_sheet.name}"
                    
                    with open(resume_path, 'wb') as f:
                        f.write(resume_file.getbuffer())
                    with open(id_path, 'wb') as f:
                        f.write(id_file.getbuffer())
                    with open(sheet_path, 'wb') as f:
                        f.write(submission_sheet.getbuffer())
                    
                    # Save submission metadata
                    submission_data = {
                        'timestamp': datetime.now().isoformat(),
                        'vendor_name': st.session_state.vendor_name,
                        'req_id': req_id,
                        'candidate_name': candidate_name,
                        'candidate_email': candidate_email,
                        'candidate_phone': candidate_phone,
                        'resume_file': str(resume_path),
                        'id_file': str(id_path),
                        'submission_sheet': str(sheet_path),
                        'additional_notes': additional_notes,
                        'status': 'submitted'
                    }
                    
                    # Update log
                    log_df = load_submissions_log()
                    new_row = pd.DataFrame([submission_data])
                    log_df = pd.concat([log_df, new_row], ignore_index=True)
                    save_submission_log(log_df)
                    
                    # Set submission success flag
                    st.session_state.submission_success = True
                    st.success(f"✅ Profile submitted successfully for {candidate_name}!")
                    st.balloons()
                    st.info("💡 To submit another candidate, please select a different requirement from the dropdown above.")
                    st.rerun()
    else:
        # Show success message and instructions
        st.success("✅ Candidate profile submitted successfully!")
        st.info("💡 To submit another candidate, please select a different requirement from the dropdown above.")
    
    # Show vendor's submissions with analytics and download
    st.divider()
    
    # Create tabs for submissions view and analytics
    tab1, tab2 = st.tabs(["📋 My Submissions", "📊 Analytics & Reports"])
    
    with tab1:
        st.subheader("📊 Your Submissions")
        log_df = load_submissions_log()
        vendor_submissions = log_df[log_df['vendor_name'] == st.session_state.vendor_name]
        
        if not vendor_submissions.empty:
            # Display submissions table
            display_df = vendor_submissions[['timestamp', 'req_id', 'candidate_name', 'status']].copy()
            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(display_df, use_container_width=True)
            
            # Download button for vendor's own submissions
            st.divider()
            st.subheader("📥 Download Your Submissions Report")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Download a detailed Excel report of all your submissions including candidate details and status.")
            with col2:
                # Generate Excel report
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Prepare data with filenames only (not full paths)
                    export_df = vendor_submissions.copy()
                    
                    # Extract just filenames from paths
                    if 'resume_file' in export_df.columns:
                        export_df['resume_file'] = export_df['resume_file'].apply(
                            lambda x: Path(x).name if pd.notna(x) else ''
                        )
                    if 'id_file' in export_df.columns:
                        export_df['id_file'] = export_df['id_file'].apply(
                            lambda x: Path(x).name if pd.notna(x) else ''
                        )
                    if 'submission_sheet' in export_df.columns:
                        export_df['submission_sheet'] = export_df['submission_sheet'].apply(
                            lambda x: Path(x).name if pd.notna(x) else ''
                        )
                    
                    # Main submissions sheet
                    export_df.to_excel(writer, sheet_name='My Submissions', index=False)
                    
                    # Summary sheet
                    summary_data = {
                        'Metric': [
                            'Total Submissions',
                            'Submitted Status',
                            'Under Review',
                            'Approved',
                            'Rejected',
                            'Unique Requirements'
                        ],
                        'Count': [
                            len(vendor_submissions),
                            len(vendor_submissions[vendor_submissions['status'] == 'submitted']),
                            len(vendor_submissions[vendor_submissions['status'] == 'under_review']),
                            len(vendor_submissions[vendor_submissions['status'] == 'approved']),
                            len(vendor_submissions[vendor_submissions['status'] == 'rejected']),
                            vendor_submissions['req_id'].nunique()
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                output.seek(0)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 Download Report",
                    data=output,
                    file_name=f"{st.session_state.vendor_name}_submissions_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.info("No submissions yet")
    
    with tab2:
        st.subheader("📊 Submission Analytics")
        
        if not vendor_submissions.empty:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Submissions", len(vendor_submissions))
            
            with col2:
                submitted_count = len(vendor_submissions[vendor_submissions['status'] == 'submitted'])
                st.metric("Submitted", submitted_count)
            
            with col3:
                approved_count = len(vendor_submissions[vendor_submissions['status'] == 'approved'])
                st.metric("Approved", approved_count)
            
            with col4:
                rejected_count = len(vendor_submissions[vendor_submissions['status'] == 'rejected'])
                st.metric("Rejected", rejected_count)
            
            st.divider()
            
            # Submissions by requirement
            st.subheader("📋 Submissions by Requirement")
            req_counts = vendor_submissions['req_id'].value_counts()
            
            # Load requirements to get job titles
            requirements = load_requirements()
            req_data = []
            for req_id, count in req_counts.items():
                job_title = requirements.get(req_id, {}).get('title', 'Unknown')
                req_data.append({
                    'Requirement': f"{req_id} - {job_title}",
                    'Submissions': count
                })
            
            req_df = pd.DataFrame(req_data)
            st.dataframe(req_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Status breakdown
            st.subheader("📈 Status Breakdown")
            status_counts = vendor_submissions['status'].value_counts()
            status_df = pd.DataFrame({
                'Status': status_counts.index,
                'Count': status_counts.values
            })
            st.dataframe(status_df, use_container_width=True)
            
            st.divider()
            
            # Recent submissions
            st.subheader("🕒 Recent Submissions (Last 5)")
            recent_df = vendor_submissions.sort_values('timestamp', ascending=False).head(5)
            recent_display = recent_df[['timestamp', 'req_id', 'candidate_name', 'status']].copy()
            recent_display['timestamp'] = pd.to_datetime(recent_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(recent_display, use_container_width=True)
            
        else:
            st.info("📊 No data available for analytics. Submit your first candidate to see analytics here!")

def admin_portal():
    """Admin management portal"""
    st.title("⚙️ Admin Portal")
    
    if st.button("Logout", key="admin_logout"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.rerun()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Manage Vendors", "📋 Manage Requirements", "📊 View Submissions", "📈 Analytics", "🎯 Vendor Limits"])
    
    with tab1:
        manage_vendors()
    
    with tab2:
        manage_requirements()
    
    with tab3:
        view_submissions()
    
    with tab4:
        show_analytics()
    
    with tab5:
        manage_vendor_limits()

def manage_vendors():
    """Manage vendor accounts"""
    st.subheader("Manage Vendor Accounts")
    
    vendors = load_vendors()
    
    # Add new vendor
    with st.expander("➕ Add New Vendor", expanded=False):
        with st.form("add_vendor"):
            vendor_username = st.text_input("Vendor Username *", placeholder="e.g., pushpaksystem")
            vendor_company = st.text_input("Company Name *", placeholder="e.g., Pushpak Systems")
            vendor_email = st.text_input("Email", placeholder="vendor@company.com")
            vendor_phone = st.text_input("Phone", placeholder="+1 (XXX) XXX-XXXX")
            vendor_password = st.text_input("Password *", type="password", placeholder="Set initial password")
            vendor_contact_person = st.text_input("Contact Person", placeholder="John Doe")
            
            if st.form_submit_button("Add Vendor"):
                if not vendor_username or not vendor_company or not vendor_password:
                    st.error("❌ Please fill all required fields (marked with *)")
                elif vendor_username in vendors:
                    st.error(f"❌ Vendor username '{vendor_username}' already exists")
                else:
                    vendors[vendor_username] = {
                        'company_name': vendor_company,
                        'email': vendor_email,
                        'phone': vendor_phone,
                        'password': vendor_password,
                        'contact_person': vendor_contact_person,
                        'status': 'active',
                        'created_date': datetime.now().isoformat(),
                        'total_submissions': 0
                    }
                    save_vendors(vendors)
                    st.success(f"✅ Vendor '{vendor_username}' added successfully!")
                    st.rerun()
    
    # Display existing vendors
    st.divider()
    st.subheader("Existing Vendors")
    
    if not vendors:
        st.info("No vendors added yet. Add your first vendor above!")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Vendors", len(vendors))
    with col2:
        active_count = len([v for v in vendors.values() if v.get('status') == 'active'])
        st.metric("Active Vendors", active_count)
    with col3:
        inactive_count = len(vendors) - active_count
        st.metric("Inactive Vendors", inactive_count)
    
    st.divider()
    
    # Display vendors in expandable cards
    for username, vendor_data in vendors.items():
        status_icon = "✅" if vendor_data.get('status') == 'active' else "❌"
        with st.expander(f"{status_icon} {vendor_data.get('company_name', username)} (@{username})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Username:** {username}")
                st.write(f"**Company:** {vendor_data.get('company_name', 'N/A')}")
                st.write(f"**Email:** {vendor_data.get('email', 'N/A')}")
                st.write(f"**Phone:** {vendor_data.get('phone', 'N/A')}")
                st.write(f"**Contact Person:** {vendor_data.get('contact_person', 'N/A')}")
                st.write(f"**Status:** {vendor_data.get('status', 'active').upper()}")
                st.write(f"**Created:** {vendor_data.get('created_date', 'N/A')[:10]}")
                
                # Count submissions
                log_df = load_submissions_log()
                if not log_df.empty:
                    submission_count = len(log_df[log_df['vendor_name'] == username])
                    st.write(f"**Total Submissions:** {submission_count}")
            
            with col2:
                # Edit form
                with st.form(f"edit_{username}"):
                    st.write("**Edit Vendor**")
                    new_company = st.text_input("Company", value=vendor_data.get('company_name', ''), key=f"company_{username}")
                    new_email = st.text_input("Email", value=vendor_data.get('email', ''), key=f"email_{username}")
                    new_phone = st.text_input("Phone", value=vendor_data.get('phone', ''), key=f"phone_{username}")
                    new_password = st.text_input("New Password", type="password", placeholder="Leave blank to keep current", key=f"pass_{username}")
                    new_status = st.selectbox("Status", ['active', 'inactive'],
                                             index=0 if vendor_data.get('status') == 'active' else 1,
                                             key=f"status_{username}")
                    
                    if st.form_submit_button("Update", key=f"update_{username}"):
                        vendors[username]['company_name'] = new_company
                        vendors[username]['email'] = new_email
                        vendors[username]['phone'] = new_phone
                        if new_password:
                            vendors[username]['password'] = new_password
                        vendors[username]['status'] = new_status
                        save_vendors(vendors)
                        st.success("✅ Updated!")
                        st.rerun()
                
                if st.button("🗑️ Delete", key=f"del_{username}"):
                    del vendors[username]
                    save_vendors(vendors)
                    st.success("✅ Deleted!")
                    st.rerun()

def manage_requirements():
    """Manage requirements section"""
    st.subheader("Manage Requirements")
    
    requirements = load_requirements()
    
    # Add new requirement
    with st.expander("➕ Add New Requirement", expanded=False):
        with st.form("add_requirement"):
            req_id = st.text_input("Requirement ID *", placeholder="REQ-001")
            title = st.text_input("Job Title *", placeholder="Senior Java Developer")
            location = st.text_input("Location *", placeholder="Phoenix, AZ")
            rate = st.number_input("Rate ($/hr) *", min_value=0.0, step=1.0, value=80.0)
            positions = st.number_input("Number of Positions *", min_value=1, step=1, value=1)
            description = st.text_area("Job Description", placeholder="Enter job requirements and description")
            skills = st.text_input("Required Skills", placeholder="Java, Spring Boot, Microservices")
            
            if st.form_submit_button("Add Requirement"):
                if not req_id or not title or not location:
                    st.error("❌ Please fill all required fields")
                elif req_id in requirements:
                    st.error(f"❌ Requirement ID {req_id} already exists")
                else:
                    requirements[req_id] = {
                        'title': title,
                        'location': location,
                        'rate': rate,
                        'positions': positions,
                        'description': description,
                        'skills': skills,
                        'status': 'active',
                        'created_date': datetime.now().isoformat()
                    }
                    save_requirements(requirements)
                    st.success(f"✅ Requirement {req_id} added successfully!")
                    st.rerun()
    
    # Display and edit existing requirements
    st.divider()
    st.subheader("Existing Requirements")
    
    if not requirements:
        st.info("No requirements added yet")
        return
    
    for req_id, req_data in requirements.items():
        with st.expander(f"{req_id} - {req_data['title']} ({req_data.get('status', 'active').upper()})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Location:** {req_data['location']}")
                st.write(f"**Rate:** ${req_data['rate']}/hr")
                st.write(f"**Positions:** {req_data['positions']}")
                st.write(f"**Skills:** {req_data.get('skills', 'N/A')}")
                st.write(f"**Description:** {req_data.get('description', 'N/A')}")
            
            with col2:
                # Edit form
                with st.form(f"edit_{req_id}"):
                    new_rate = st.number_input("Rate", value=float(req_data['rate']), key=f"rate_{req_id}")
                    new_positions = st.number_input("Positions", value=int(req_data['positions']), key=f"pos_{req_id}")
                    new_status = st.selectbox("Status", ['active', 'closed'], 
                                             index=0 if req_data.get('status') == 'active' else 1,
                                             key=f"status_{req_id}")
                    
                    if st.form_submit_button("Update"):
                        requirements[req_id]['rate'] = new_rate
                        requirements[req_id]['positions'] = new_positions
                        requirements[req_id]['status'] = new_status
                        save_requirements(requirements)
                        st.success("✅ Updated!")
                        st.rerun()
                
                if st.button("🗑️ Delete", key=f"del_{req_id}"):
                    del requirements[req_id]
                    save_requirements(requirements)
                    st.success("✅ Deleted!")
                    st.rerun()

def view_submissions():
    """View all submissions with detailed view and downloads"""
    st.subheader("All Submissions")
    
    log_df = load_submissions_log()
    
    if log_df.empty:
        st.info("No submissions yet")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        vendor_filter = st.multiselect("Filter by Vendor", options=log_df['vendor_name'].unique())
    with col2:
        req_filter = st.multiselect("Filter by Requirement", options=log_df['req_id'].unique())
    with col3:
        status_filter = st.multiselect("Filter by Status", options=log_df['status'].unique())
    
    # Apply filters
    filtered_df = log_df.copy()
    if vendor_filter:
        filtered_df = filtered_df[filtered_df['vendor_name'].isin(vendor_filter)]
    if req_filter:
        filtered_df = filtered_df[filtered_df['req_id'].isin(req_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    
    # Display submissions count
    st.write(f"**Total Submissions:** {len(filtered_df)}")
    
    # Download options
    col1, col2 = st.columns(2)
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"submissions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Generate Excel report
        excel_data = generate_excel_report(filtered_df)
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_data,
            file_name=f"submissions_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.divider()
    
    # Detailed view of each submission
    st.subheader("Submission Details")
    
    for idx, row in filtered_df.iterrows():
        with st.expander(f"📋 {row['candidate_name']} - {row['req_id']} ({row['vendor_name']})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Candidate:** {row['candidate_name']}")
                st.write(f"**Vendor:** {row['vendor_name']}")
                st.write(f"**Requirement:** {row['req_id']}")
                st.write(f"**Submitted:** {pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Status:** {row['status']}")
                
                # Show additional info if available
                if 'candidate_email' in row and pd.notna(row.get('candidate_email')):
                    st.write(f"**Email:** {row['candidate_email']}")
                if 'candidate_phone' in row and pd.notna(row.get('candidate_phone')):
                    st.write(f"**Phone:** {row['candidate_phone']}")
                if 'additional_notes' in row and pd.notna(row.get('additional_notes')):
                    st.write(f"**Notes:** {row['additional_notes']}")
            
            with col2:
                st.write("**📎 Attachments:**")
                
                # Download resume
                if pd.notna(row.get('resume_file')) and Path(row['resume_file']).exists():
                    with open(row['resume_file'], 'rb') as f:
                        st.download_button(
                            label="📄 Download Resume",
                            data=f.read(),
                            file_name=Path(row['resume_file']).name,
                            mime="application/octet-stream",
                            key=f"resume_{idx}"
                        )
                
                # Download ID
                if pd.notna(row.get('id_file')) and Path(row['id_file']).exists():
                    with open(row['id_file'], 'rb') as f:
                        st.download_button(
                            label="🆔 Download ID Photo",
                            data=f.read(),
                            file_name=Path(row['id_file']).name,
                            mime="application/octet-stream",
                            key=f"id_{idx}"
                        )
                
                # Download submission sheet
                if pd.notna(row.get('submission_sheet')) and Path(row['submission_sheet']).exists():
                    with open(row['submission_sheet'], 'rb') as f:
                        st.download_button(
                            label="📊 Download Submission Sheet",
                            data=f.read(),
                            file_name=Path(row['submission_sheet']).name,
                            mime="application/octet-stream",
                            key=f"sheet_{idx}"
                        )
                
                st.divider()
                
                # Delete submission with confirmation
                if f'confirm_delete_{idx}' not in st.session_state:
                    st.session_state[f'confirm_delete_{idx}'] = False
                
                if not st.session_state[f'confirm_delete_{idx}']:
                    # Show delete button
                    if st.button("🗑️ Delete Submission", key=f"delete_{idx}", type="secondary", use_container_width=True):
                        st.session_state[f'confirm_delete_{idx}'] = True
                        st.rerun()
                else:
                    # Show confirmation dialog
                    st.warning(f"⚠️ **Are you sure you want to delete this submission?**\n\nCandidate: **{row['candidate_name']}**\n\nThis will permanently delete:\n- Submission record\n- All uploaded files (resume, ID, submission sheet)\n- Complete candidate folder")
                    
                    col_confirm1, col_confirm2 = st.columns(2)
                    with col_confirm1:
                        if st.button("✅ Yes, Delete", key=f"confirm_yes_{idx}", type="primary", use_container_width=True):
                            # Delete the submission from log
                            log_df_updated = log_df[log_df.index != idx].copy()
                            save_submission_log(log_df_updated)
                            
                            # Delete entire candidate folder and all files
                            deleted_files = False
                            try:
                                # Get the candidate folder path (parent directory of the files)
                                if pd.notna(row.get('resume_file')):
                                    candidate_folder = Path(row['resume_file']).parent
                                    if candidate_folder.exists():
                                        # Delete entire folder with all contents
                                        import shutil
                                        shutil.rmtree(candidate_folder)
                                        deleted_files = True
                            except Exception as e:
                                st.error(f"❌ Error deleting files: {str(e)}")
                            
                            # Reset confirmation state and clear all delete-related session states
                            st.session_state[f'confirm_delete_{idx}'] = False
                            
                            # Show success message
                            if deleted_files:
                                st.success(f"✅ Submission for **{row['candidate_name']}** and all associated files have been permanently deleted!")
                            else:
                                st.success(f"✅ Submission record for **{row['candidate_name']}** has been removed.")
                            
                            # Force page refresh
                            st.rerun()
                    
                    with col_confirm2:
                        if st.button("❌ Cancel", key=f"confirm_no_{idx}", type="secondary", use_container_width=True):
                            st.session_state[f'confirm_delete_{idx}'] = False
                            st.rerun()

def generate_excel_report(df):
    """Generate Excel report with all submission details"""
    from io import BytesIO
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    
    # Create a BytesIO buffer
    output = BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Prepare data for Excel
        report_df = df.copy()
        
        # Format timestamp
        if 'timestamp' in report_df.columns:
            report_df['timestamp'] = pd.to_datetime(report_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Select and rename columns for report
        columns_to_include = ['timestamp', 'vendor_name', 'req_id', 'candidate_name',
                             'candidate_email', 'candidate_phone', 'status']
        
        # Only include columns that exist
        columns_to_include = [col for col in columns_to_include if col in report_df.columns]
        report_df = report_df[columns_to_include]
        
        # Rename columns for better readability
        column_names = {
            'timestamp': 'Submission Date',
            'vendor_name': 'Vendor',
            'req_id': 'Requirement ID',
            'candidate_name': 'Candidate Name',
            'candidate_email': 'Email',
            'candidate_phone': 'Phone',
            'status': 'Status'
        }
        report_df = report_df.rename(columns=column_names)
        
        # Write to Excel
        report_df.to_excel(writer, sheet_name='Submissions', index=False)
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Submissions']
        
        # Style the header row
        header_fill = PatternFill(start_color='0066CC', end_color='0066CC', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF')
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Submissions', 'Unique Vendors', 'Unique Requirements', 'Report Generated'],
            'Value': [
                len(df),
                df['vendor_name'].nunique(),
                df['req_id'].nunique(),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Style summary sheet
        summary_sheet = writer.sheets['Summary']
        for cell in summary_sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        for column in summary_sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            summary_sheet.column_dimensions[column_letter].width = adjusted_width
    
    # Get the value from the buffer
    output.seek(0)
    return output.getvalue()

def show_analytics():
    """Show analytics dashboard"""
    st.subheader("Analytics Dashboard")
    
    log_df = load_submissions_log()
    requirements = load_requirements()
    
    if log_df.empty:
        st.info("No data available for analytics")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Submissions", len(log_df))
    with col2:
        st.metric("Active Requirements", len([r for r in requirements.values() if r.get('status') == 'active']))
    with col3:
        st.metric("Unique Vendors", log_df['vendor_name'].nunique())
    
    st.divider()
    
    # Submissions by vendor
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Submissions by Vendor")
        vendor_counts = log_df['vendor_name'].value_counts()
        st.bar_chart(vendor_counts)
    
    with col2:
        st.subheader("Submissions by Requirement")
        req_counts = log_df['req_id'].value_counts()
        st.bar_chart(req_counts)
    
    # Submissions over time
    st.subheader("Submissions Timeline")
    log_df['date'] = pd.to_datetime(log_df['timestamp']).dt.date
    timeline = log_df.groupby('date').size()
    st.line_chart(timeline)

def manage_vendor_limits():
    """Manage vendor-specific submission limits"""
    st.subheader("🎯 Manage Vendor Submission Limits")
    st.write("Grant additional submission slots to specific vendors for specific requirements.")
    
    vendors = load_vendors()
    requirements = load_requirements()
    vendor_limits = load_vendor_limits()
    
    if not vendors:
        st.warning("⚠️ No vendors available. Please add vendors first.")
        return
    
    if not requirements:
        st.warning("⚠️ No requirements available. Please add requirements first.")
        return
    
    # Display current custom limits
    st.subheader("📋 Current Custom Limits")
    if vendor_limits:
        limits_data = []
        for key, limit in vendor_limits.items():
            vendor_name, req_id = key.split('|')
            vendor_company = vendors.get(vendor_name, {}).get('company', vendor_name)
            req_title = requirements.get(req_id, {}).get('title', req_id)
            limits_data.append({
                'Vendor': vendor_company,
                'Requirement': f"{req_id} - {req_title}",
                'Custom Limit': limit,
                'Key': key
            })
        
        limits_df = pd.DataFrame(limits_data)
        
        # Display with delete option
        for idx, row in limits_df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
            with col1:
                st.write(f"**{row['Vendor']}**")
            with col2:
                st.write(row['Requirement'])
            with col3:
                st.write(f"Limit: **{row['Custom Limit']}**")
            with col4:
                if st.button("🗑️", key=f"delete_{row['Key']}", help="Remove custom limit"):
                    del vendor_limits[row['Key']]
                    save_vendor_limits(vendor_limits)
                    st.success("✅ Custom limit removed. Vendor will now have default limit of 2.")
                    st.rerun()
    else:
        st.info("ℹ️ No custom limits set. All vendors have the default limit of 2 submissions per requirement.")
    
    st.divider()
    
    # Add new custom limit
    st.subheader("➕ Set Custom Limit")
    
    with st.form("set_vendor_limit"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Vendor selection
            vendor_options = {v: vendors[v].get('company', v) for v in vendors.keys()}
            selected_vendor = st.selectbox(
                "Select Vendor *",
                options=list(vendor_options.keys()),
                format_func=lambda x: vendor_options[x]
            )
        
        with col2:
            # Requirement selection
            req_options = {r: f"{r} - {requirements[r]['title']}" for r in requirements.keys()}
            selected_req = st.selectbox(
                "Select Requirement *",
                options=list(req_options.keys()),
                format_func=lambda x: req_options[x]
            )
        
        # Get current submission count
        if selected_vendor and selected_req:
            current_count = count_vendor_submissions(selected_vendor, selected_req)
            current_limit = get_vendor_submission_limit(selected_vendor, selected_req)
            st.info(f"📊 Current Status: **{current_count}/{current_limit}** submissions")
        
        # New limit input
        new_limit = st.number_input(
            "New Submission Limit *",
            min_value=1,
            max_value=50,
            value=5,
            step=1,
            help="Set the maximum number of submissions this vendor can make for this requirement"
        )
        
        st.write("**Note:** Setting a custom limit will override the default limit of 2 submissions.")
        
        submitted = st.form_submit_button("Set Custom Limit")
        
        if submitted:
            if not selected_vendor or not selected_req:
                st.error("❌ Please select both vendor and requirement")
            else:
                set_vendor_submission_limit(selected_vendor, selected_req, new_limit)
                vendor_company = vendors[selected_vendor].get('company', selected_vendor)
                req_title = requirements[selected_req]['title']
                st.success(f"✅ Custom limit of **{new_limit}** submissions set for **{vendor_company}** on requirement **{req_title}**")
                st.rerun()
    
    st.divider()
    
    # Show vendor submission status
    st.subheader("📊 Vendor Submission Status")
    
    log_df = load_submissions_log()
    
    if not log_df.empty:
        status_data = []
        for vendor_name in vendors.keys():
            vendor_company = vendors[vendor_name].get('company', vendor_name)
            for req_id in requirements.keys():
                req_title = requirements[req_id]['title']
                submission_count = count_vendor_submissions(vendor_name, req_id)
                submission_limit = get_vendor_submission_limit(vendor_name, req_id)
                
                if submission_count > 0:  # Only show if vendor has made submissions
                    status_data.append({
                        'Vendor': vendor_company,
                        'Requirement': f"{req_id} - {req_title}",
                        'Submissions': f"{submission_count}/{submission_limit}",
                        'Status': '🔴 At Limit' if submission_count >= submission_limit else '🟢 Available'
                    })
        
        if status_data:
            status_df = pd.DataFrame(status_data)
            st.dataframe(status_df, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No submissions yet")
    else:
        st.info("ℹ️ No submissions yet")


def main():
    """Main application"""
    st.set_page_config(
        page_title="Vendor Portal",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.user_type == "vendor":
        vendor_portal()
    elif st.session_state.user_type == "admin":
        admin_portal()

if __name__ == "__main__":
    main()

# Made with Bob
