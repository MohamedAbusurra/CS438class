import pytest
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from models.TaskManagement import Task  

@pytest.mark.parametrize("importance", ["high", "normal"])
@pytest.mark.parametrize("status", ["not begun", "in progress", "finished"])
def test_task_init_valid_values(importance, status):
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
def test_task_init_invalid_importance_raises(bad_importance):
    with pytest.raises(Exception, match="Bad importance"):
        Task(title="Invalid importance", projectId=1, importance=bad_importance)


@pytest.mark.parametrize("bad_status", ["", "paused", None])
def test_task_init_invalid_status_raises(bad_status):
    with pytest.raises(Exception, match="Invalid status"):
        Task(title="Invalid status", projectId=1, taskStatus=bad_status)


def test_to_dict_serialization():
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
    task.id = 42
    task.created_at = now

    task_dict = task.to_dict()
    assert task_dict["title"] == "Serialize test"
    assert task_dict["importance"] == "high"
    assert task_dict["is_high_importance"] is True
    assert task_dict["due_date"] == "2023-01-01"
    assert task_dict["actual_start_datetime"] == "2023-01-01 12:00:00"


@patch("models.task.db")
def test_create_task_success(mock_db):
    mock_session = MagicMock()
    mock_db.session = mock_session

    task = Task.create_task(
        title="Create method test",
        project_id=99,
        importance="normal",
        status="not begun"
    )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert task.taskTitle == "Create method test"
    assert task.project_id == 99


@patch("models.task.db")
def test_update_task_fields(mock_db):
    task = Task(title="Initial", projectId=1)
    updated = task.update(
        title="Updated",
        importance="high",
        status="in progress",
        estimated_duration=10
    )

    assert updated.taskTitle == "Updated"
    assert updated.importance == "high"
    assert updated.status == "in progress"
    assert updated.estimatedDuration == 10
    mock_db.session.commit.assert_called_once()


@patch("models.task.db")
def test_update_invalid_importance_raises(mock_db):
    task = Task(title="Update error", projectId=1)
    with pytest.raises(Exception, match="Bad importance"):
        task.update(importance="invalid")


@patch("models.task.db")
def test_update_invalid_status_raises(mock_db):
    task = Task(title="Update error", projectId=1)
    with pytest.raises(Exception, match="Invalid status"):
        task.update(status="paused")


@patch("models.task.db")
def test_delete_task(mock_db):
    task = Task(title="Delete test", projectId=123)
    project_id = task.delete()

    assert project_id == 123
    mock_db.session.delete.assert_called_once_with(task)
    mock_db.session.commit.assert_called_once()


@patch("models.task.Task.query")
def test_get_project_tasks(mock_query):
    mock_query.filter_by.return_value.all.return_value = ["task1", "task2"]
    tasks = Task.getProjectTasks(project_id=42)
    assert tasks == ["task1", "task2"]