# CMT - Collaboration Management Tool

CMT is a simple collaboration management tool that allows users to create projects, manage tasks, and share files. It is built using Flask and SQLAlchemy, with a focus on simplicity and ease of use for beginners.

## Recent Updates

The project has been significantly simplified to make it more beginner-friendly:

- **Simplified Templates**: All HTML templates have been simplified to use basic HTML elements without complex frameworks.
- **Minimal CSS**: Replaced Bootstrap with simple, inline CSS for basic styling.
- **Basic JavaScript**: Reduced JavaScript to only essential functionality.
- **Removed Complexity**: Eliminated milestone functionality and simplified the project structure.
- **Beginner-Friendly Forms**: Replaced complex modals with simple, easy-to-understand forms.

## Features

### Project Management
- Create projects with name, description, start date, and expected end date
- View all projects in a centralized list
- Delete projects when they're no longer needed
- Track project status

### Task Management
- Create tasks with title, description, importance, and status
- Assign tasks to users
- Track task progress and deadlines
- Set estimated duration and actual start/end times

### File Management
- Upload files to the system
- Associate files with specific projects
- Download files for offline use
- Delete files when they're no longer needed
- Automatic file versioning

### Reporting
- Generate performance reports in PDF or CSV format
- Include completed tasks, missed deadlines, and individual contributions

## Technology Stack

- **Backend**: Python with Flask framework
- **Frontend**: Simple HTML, CSS, and minimal JavaScript
- **Database**: SQLite with SQLAlchemy ORM
- **File Storage**: Local file system

## Installation

### Prerequisites
- Python 3.9 or higher
- pip or pipenv (for package management)

### Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/MohamedAbusurra/CS438class.git
   cd CMT
   ```

2. Set up a virtual environment using pipenv:
   ```
   pipenv install
   ```

3. Activate the virtual environment:
   ```
   pipenv shell
   ```

4. Install the required dependencies:
   ```
   pipenv install flask flask-sqlalchemy
   ```

5. Run the application:
   ```
   python run.py
   ```

6. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage Guide

### Creating a New Project
1. Navigate to the "Projects" page and click "Create New Project"
2. Fill in the project details (name, description, start date, etc.)
3. Click "Create Project" to save the new project

### Managing Tasks
1. Go to a project's detail page and click "View Tasks"
2. Use the "Create New Task" button to add tasks
3. Edit or delete tasks using the action buttons
4. Track task status and progress

### Managing Files
1. Go to the "Files" page from the navigation bar
2. Use the "Upload File" button to add new files
3. Associate files with projects during upload
4. Use the action buttons to download or delete files

### Project Details
1. Click on a project name from the Projects list to view its details
2. See all files associated with the project
3. Upload files directly from the project page

## Project Structure

```
CMT/
├── app.py                     # Main application file
├── run.py                     # Script to run the application
├── models/                    # Database models
│   ├── __init__.py           # Package initialization
│   ├── database.py           # Database configuration
│   ├── user.py               # User model
│   ├── project.py            # Project model
│   ├── task.py               # Task model
│   ├── file.py               # File model
│   ├── file_version.py       # FileVersion model
│   └── report.py             # Report model
├── templates/                 # HTML templates
│   ├── base.html             # Base template with layout
│   ├── projects.html         # Projects list template
│   ├── create_project.html   # Project creation template
│   ├── project.html          # Project details template
│   ├── project_details.html  # Project details template
│   ├── task.html             # Task management template
│   ├── files.html            # File management template
│   ├── project_reports.html  # Reports template
│   └── errors/               # Error page templates
│       ├── 403.html          # Forbidden error template
│       └── 404.html          # Not found error template
├── static/                    # Static files
│   ├── css/                  # CSS files
│   │   └── style.css         # Main stylesheet
│   └── js/                   # JavaScript files
│       └── main.js           # Main JavaScript file
└── uploads/                   # Uploaded files directory
```





## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Flask for the web framework
- SQLAlchemy for the ORM
