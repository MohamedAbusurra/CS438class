import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from models.AnalysisandReporting import Report  


# ---------- Fixtures ----------

@pytest.fixture
def valid_filters():
    return {
        "include_completed_tasks": True,
        "includeMissedDeadlines": False,
        "include_contributions": True,
        "format": "pdf"
    }


# ---------- Initialization Tests ----------

def test_valid_report_creation(valid_filters):
    report = Report(project_id=1, reportType="performance", created_by_id=42, filters=valid_filters)

    assert report.project_id == 1
    assert report.created_by_id == 42
    assert report.filters == valid_filters
    assert report.status.strip() == Report.STATUS_PENDING.strip()
    assert report.progress == 0


@pytest.mark.parametrize("bad_type", ["summary", "", None])
def test_invalid_report_type_raises(bad_type):
    with pytest.raises(ValueError, match="Invalid report type"):
        Report(project_id=1, reportType=bad_type)


def test_default_filters_when_none_provided():
    report = Report(project_id=2)
    assert report.filters["include_completed_tasks"] is True
    assert report.filters["format"] == "pdf"


# ---------- Filter Property Tests ----------

def test_filters_set_and_get_as_dict(valid_filters):
    report = Report(project_id=3, filters=valid_filters)
    assert isinstance(report.filters, dict)
    assert report.filters["format"] == "pdf"


def test_filters_broken_json_returns_empty(monkeypatch):
    report = Report(project_id=4)
    monkeypatch.setattr(report, "_filters", "bad json!")
    assert report.filters == {}


# ---------- Progress Update Tests ----------

@pytest.mark.parametrize("progress_value", [0, 50, 100])
def test_update_progress_valid(progress_value):
    report = Report(project_id=1)
    report.update_progress(progress_value)

    assert report.progress == progress_value
    if progress_value == 100:
        assert report.status.strip() == Report.STATUS_COMPLETED.strip()
        assert report.completed_at is not None


@pytest.mark.parametrize("bad_progress", [-1, 101, 1000])
def test_update_progress_invalid(bad_progress):
    report = Report(project_id=1)
    with pytest.raises(ValueError, match="progress must be like 0 - 100"):
        report.update_progress(bad_progress)


def test_mark_as_failed_sets_status_and_time():
    report = Report(project_id=1)
    report.mark_as_failed()
    assert report.status.strip() == Report.STATUS_FAILED.strip()
    assert report.completed_at is not None


# ---------- to_dict() Tests ----------

def test_to_dict_serialization_fields(valid_filters):
    now = datetime(2024, 1, 1, 10, 30, tzinfo=timezone.utc)

    report = Report(project_id=1, filters=valid_filters)
    report.id = 123
    report.created_by_id = 7
    report.created_at = now
    report.completed_at = now
    report.file_path = "/some/file.pdf"
    report.update_progress(100)

    data = report.to_dict()

    assert data["id"] == 123
    assert data["project_id"] == 1
    assert data["report_type"] == "performance"
    assert data["file_path"] == "/some/file.pdf"
    assert data["status"].strip() == "completed"
    assert data["filters"] == valid_filters


# ---------- create_report() Tests ----------

@patch("models.ReportManagement.report.db")
def test_create_report_saves_to_db(mock_db):
    mock_session = MagicMock()
    mock_db.session = mock_session

    report = Report.create_report(project_id=11)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert report.project_id == 11
    assert report.status.strip() == Report.STATUS_PENDING.strip()


# ---------- get_project_reports() Tests ----------

@patch("models.ReportManagement.report.Report.query")
def test_get_project_reports_returns_list(mock_query):
    mock_query.filter_by.return_value.order_by.return_value.all.return_value = ["r1", "r2"]
    reports = Report.get_project_reports(project_id=99)
    assert reports == ["r1", "r2"]
    mock_query.filter_by.assert_called_once_with(project_id=99)


# ---------- get_status() Tests ----------

def test_get_status_incomplete_report():
    report = Report(project_id=1)
    report.update_progress(50)
    status = report.get_status()

    assert status["status"].strip() == "in progress"
    assert status["progress"] == 50
    assert status["completed_at"] is None
    assert status["file_path"] is None


def test_get_status_completed_report():
    report = Report(project_id=1)
    report.file_path = "/path/to/report.pdf"
    report.update_progress(100)
    status = report.get_status()

    assert status["status"].strip() == "completed"
    assert status["file_path"] == "/path/to/report.pdf"
    assert status["completed_at"] is not None