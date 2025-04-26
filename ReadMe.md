# CMT - Collaboration Management Tool

CMT is a simple collaboration management tool that allows users to create projects, manage tasks, and share files. It is built using Flask and SQLAlchemy.

## Recent Updates

The project has been significantly simplified to make it more beginner-friendly:

- **Simplified Templates** : we have make all html templates to be simple and easy to understand.
**Minimal CSS**: we have remove bootstrap  with simple inline css for basic style.
- **Basic JavaScript** : make javascript for only important functionality.
## Features

### Project Management
- Create projects with name, description, start date, and expected end date .
- View all projects in a central list .
- Delete projects .
- Track project status.

### Task Management
- Create tasks with title, description, importance, and status.
- Assign tasks to team member.
- Track task progress and deadlines .
- Set estimated duration and actual start/end times .

### File Management
- Upload files to the system .
- link uploaded files with specific projects .
- Download files for offline use .
- Delete files .
- Automatic file versioning .

### Reporting
- Generate performance reports in PDF or CSV format .
- Include completed tasks, missed deadlines, and individual contributions .

## Technology Stack

- **Backend**: Python with Flask framework .
- **Frontend**: Simple HTML, CSS, and minimal JavaScript .
- **Database**: SQLite with SQLAlchemy ORM .
- **File Storage**: Local file system .

## Installation

### Prerequisites
- Python 3.9 or higher .
- pipenv (for package management) .

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

6. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```



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
