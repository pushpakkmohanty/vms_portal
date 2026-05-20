# Vendor Profile Submission Portal

A Streamlit-based web application for vendors to submit candidate profiles and administrators to manage job requirements.

## Features

### Vendor Features
- 🔐 Simple vendor login (name-based)
- 📋 View active job requirements with rates and positions
- 📤 Submit candidate profiles with:
  - Resume (PDF, DOC, DOCX)
  - Candidate ID photo (JPG, PNG)
  - Submission Excel sheet (XLSX, XLS)
- 📊 View submission history
- ⚠️ Maximum 2 submissions per requirement per vendor

### Admin Features
- 🔐 Password-protected admin access
- ➕ Add new job requirements
- ✏️ Update requirement rates and number of positions
- 🔄 Activate/deactivate requirements
- 📊 View all vendor submissions
- 📈 Analytics dashboard with:
  - Submission statistics
  - Vendor activity tracking
  - Timeline visualization
- 📥 Export submissions to CSV

## Installation

### Local Setup

1. **Clone or navigate to the portal directory:**
   ```bash
   cd portal
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Access the portal:**
   - Open your browser to `http://localhost:8501`

### Default Admin Credentials
- **Password:** `admin123`
- ⚠️ **Important:** Change this in production by modifying the `ADMIN_PASSWORD` variable in `app.py`

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Steps

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Vendor Portal"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/vendor-portal.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `portal/app.py`
   - Click "Deploy"

3. **Configure secrets (optional):**
   - In Streamlit Cloud dashboard, go to app settings
   - Add secrets for production:
     ```toml
     [passwords]
     admin = "your_secure_password_here"
     ```

### Important Notes for Production

1. **Security:**
   - Change the default admin password
   - Consider implementing proper authentication (OAuth, JWT)
   - Use environment variables for sensitive data

2. **Data Persistence:**
   - Current setup uses local file storage
   - For production, consider:
     - Cloud storage (AWS S3, Google Cloud Storage)
     - Database (PostgreSQL, MongoDB)
     - Streamlit's built-in data storage

3. **File Storage:**
   - Uploaded files are stored in `portal_data/uploads/`
   - Ensure adequate storage space
   - Implement file cleanup policies

## Directory Structure

```
portal/
├── app.py                      # Main application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .streamlit/
│   └── config.toml            # Streamlit configuration
└── portal_data/               # Created at runtime
    ├── requirements.json      # Job requirements database
    ├── submissions_log.csv    # Submission tracking
    ├── submissions/           # Submission metadata
    └── uploads/               # Uploaded files
        └── [vendor_name]/
            └── [req_id]/
                └── [timestamp]/
                    ├── resume_*
                    ├── id_*
                    └── submission_*
```

## Usage Guide

### For Vendors

1. **Login:**
   - Enter your vendor name
   - Click "Login as Vendor"

2. **Submit Profile:**
   - Select a requirement from the dropdown
   - Fill in candidate details
   - Upload required documents:
     - Resume
     - Candidate ID photo
     - Submission Excel sheet
   - Add any additional notes
   - Click "Submit Profile"

3. **Track Submissions:**
   - View your submission history at the bottom of the page
   - Monitor submission status

### For Administrators

1. **Login:**
   - Enter admin password
   - Click "Login as Admin"

2. **Manage Requirements:**
   - Go to "Manage Requirements" tab
   - Add new requirements with:
     - Requirement ID
     - Job title
     - Location
     - Rate per hour
     - Number of positions
     - Job description and skills
   - Update existing requirements
   - Activate/deactivate requirements
   - Delete requirements if needed

3. **View Submissions:**
   - Go to "View Submissions" tab
   - Filter by vendor, requirement, or status
   - Download submissions as CSV

4. **Analytics:**
   - Go to "Analytics" tab
   - View submission statistics
   - Monitor vendor activity
   - Track submissions over time

## Customization

### Changing Admin Password
Edit `app.py` line 28:
```python
ADMIN_PASSWORD = "your_new_password"
```

### Adjusting Submission Limits
Edit `app.py` line 147 to change the limit:
```python
if submission_count >= 2:  # Change 2 to your desired limit
```

### Modifying File Upload Limits
Edit `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 50  # Size in MB
```

## Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Dependencies Not Installing
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Data Not Persisting
- Check write permissions for `portal_data/` directory
- Ensure sufficient disk space

## Support

For issues or questions:
1. Check the logs in the terminal
2. Review Streamlit documentation: [docs.streamlit.io](https://docs.streamlit.io)
3. Contact the administrator

## License

Internal use only - American Express Vendor Portal