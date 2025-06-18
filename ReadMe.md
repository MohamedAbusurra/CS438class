# CMT - Collaboration Management Tool

CMT هي أداة بسيطة لإدارة التعاون، تتيح للمستخدمين إنشاء المشاريع وإدارة المهام ومشاركة الملفات. صُممت باستخدام Flask وSQLAlchemy، مع التركيز على البساطة وسهولة الاستخدام 


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
   python app.py
   ```

6. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

