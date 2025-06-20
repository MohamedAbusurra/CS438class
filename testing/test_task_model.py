"""
Unit tests for Task class in Task Management module.

Covers:
- Task constructor with valid/invalid values
- to_dict serialization logic
- Task creation, update, delete
- DB interaction with patching
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from models.TaskManagement.task import Task


@pytest.mark.parametrize("importance", ["high", "normal"])
@pytest.mark.parametrize("status", ["not begun", "in progress", "finished"])
def test_task_creation_valid(importance, status):
    task = Task(
        title="Write tests",
        projectId=1,
        importance=importance,
        taskStatus=status
    )
    assert task.taskTitle == "Write tests"
    assert task.importance == importance
    assert task.status == status
    assert task.project_id == 1


@pytest.mark.parametrize("bad_importance", ["low", "", None])
def test_task_invalid_importance_raises(bad_importance):
    with pytest.raises(Exception, match="Bad importance"):
        Task(title="Invalid importance", projectId=1, importance=bad_importance)


@pytest.mark.parametrize("bad_status", ["", "paused", None])
def test_task_invalid_status_raises(bad_status):
    with pytest.raises(Exception, match="Invalid status"):
        Task(title="Invalid status", projectId=1, taskStatus=bad_status)


def test_to_dict_serializes_fields():
    now = datetime(2023, 1, 1, 12, 0, 0)
    task = Task(
        title="Serialize test",
        projectId=1,
        importance="high",
        taskStatus="not begun",
        due_date=now,
        createdBy=1,
        startDate=now,
        actualStart=now,
        actualEnd=now,
    )
    task.id = 101
    task.created_at = now

    result = task.to_dict()
    assert result["title"] == "Serialize test"
    assert result["importance"] == "high"
    assert result["is_high_importance"] is True
    assert result["due_date"] == "2023-01-01"
    assert result["actual_start_datetime"] == "2023-01-01 12:00:00"


@patch("models.task.db")
def test_create_task_saves_to_db(mock_db):
    mock_session = MagicMock()
    mock_db.session = mock_session

    task = Task.create_task(
        title="DB Test",
        project_id=99,
        importance="normal",
        status="not begun"
    )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert task.taskTitle == "DB Test"
    assert task.project_id == 99


@patch("models.task.db")
def test_update_task_valid_fields(mock_db):
    task = Task(title="Old", projectId=1)
    updated = task.update(
        title="New",
        importance="high",
        status="in progress",
        estimated_duration=8
    )
    assert updated.taskTitle == "New"
    assert updated.importance == "high"
    assert updated.status == "in progress"
    assert updated.estimatedDuration == 8
    mock_db.session.commit.assert_called_once()


@patch("models.task.db")
def test_update_invalid_importance_raises(mock_db):
    task = Task(title="Err", projectId=1)
    with pytest.raises(Exception, match="Bad importance"):
        task.update(importance="very high")


@patch("models.task.db")
def test_update_invalid_status_raises(mock_db):
    task = Task(title="Err", projectId=1)
    with pytest.raises(Exception, match="Invalid status"):
        task.update(status="paused")


@patch("models.task.db")
def test_task_delete_calls_db(mock_db):
    task = Task(title="To delete", projectId=555)
    result = task.delete()
    assert result == 555
    mock_db.session.delete.assert_called_once_with(task)
    mock_db.session.commit.assert_called_once()


@patch("models.task.Task.query")
def test_get_project_tasks_returns_results(mock_query):
    mock_query.filter_by.return_value.all.return_value = ["task1", "task2"]
    tasks = Task.getProjectTasks(project_id=12)
    assert tasks == ["task1", "task2"]







# beffoer Code Smell
def __init__(self, ...):
    self.project_id = project_id
    self.file_name = file_name

    if file_size > 100 * 1024 * 1024:
        raise ValueError(f"file size exceeds...")
    
    if file_extension not in self.SUPPORTED_TYPES:
        raise ValueError(f" file type bnot good")

# after (Refactored)
def __init__(self, ...):
    self._validate_file_size(file_size)
    self._validate_file_type(file_type)
    self._initialize_attributes(...)

def _validate_file_size(self, size):
    if size > self.MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds {self.MAX_FILE_SIZE // (1024 * 1024)} MB")
def _validate_file_type(self, file_type):
    extension = self._fileTypeTolowerNodot(file_type)
    if extension not in self.SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {file_type}")