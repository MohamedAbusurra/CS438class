import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from models.ProjectManagement import Milestone


def future_date(days=7):
    return (datetime.now(timezone.utc) + timedelta(days=days)).date()

def past_date(days=7):
    return (datetime.now(timezone.utc) - timedelta(days=days)).date()


# ---------- Dashboard Progress Scenarios ----------

def test_progress_no_tasks_sets_zero():
    milestone = Milestone(title="Setup", project_id=1, due_date=future_date())
    milestone.tasks = []
    percentage = milestone.update_completion()
    assert percentage == 0.0
    assert milestone.status == Milestone.STATUS_NOT_STARTED


def test_progress_all_tasks_completed_sets_100():
    milestone = Milestone(title="Phase 1", project_id=1, due_date=future_date())
    milestone.tasks = [MagicMock(status="completed"), MagicMock(status="completed")]
    percentage = milestone.update_completion()
    assert percentage == 100.0
    assert milestone.status == Milestone.STATUS_COMPLETED


def test_progress_partial_tasks_sets_in_progress():
    milestone = Milestone(title="Phase 2", project_id=1, due_date=future_date())
    milestone.tasks = [MagicMock(status="completed"), MagicMock(status="in_progress")]
    percentage = milestone.update_completion()
    assert 0 < percentage < 100
    assert milestone.status == Milestone.STATUS_IN_PROGRESS


def test_progress_zero_tasks_past_due_sets_delayed():
    milestone = Milestone(title="Phase 3", project_id=1, due_date=past_date())
    milestone.tasks = []
    percentage = milestone.update_completion()
    assert percentage == 0.0
    assert milestone.status == Milestone.STATUS_DELAYED


def test_progress_partial_tasks_past_due_sets_delayed():
    milestone = Milestone(title="Phase 4", project_id=1, due_date=past_date())
    milestone.tasks = [MagicMock(status="completed"), MagicMock(status="in_progress")]
    percentage = milestone.update_completion()
    assert 0 < percentage < 100
    assert milestone.status == Milestone.STATUS_DELAYED