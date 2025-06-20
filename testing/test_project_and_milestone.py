"""
covers every public method 
"""
from datetime import date, timedelta

import pytest
from unittest.mock import patch

from models.ProjectManagement.project import Project  
from models.ProjectManagement.milestone import Milestone  
from models.database import db



def _today(offset: int = 0):
    return date.today() + timedelta(days=offset)


 # project section
def test_create_project_and_to_dict(test_app):
    """create_project → row exists; to_dict returns the same data."""
    with test_app.app_context():
        proj = Project.create_project(
            project_name="unit-proj",

            description="pytest project",
            start_date=_today(),
            expected_end_date=_today(30),
            status="active",

            created_by_id=None,
        )  # uses constructor + sql commit

        assert proj.id is not None

        as_dict = proj.to_dict()
        assert as_dict["project_name"]   == "unit-proj"
        assert as_dict["status"] ==   "active"


def test_get_milestones_sorted_and_active(test_app):

    """get_milestones must be sorted by due_date  and active one detected"""
    with test_app.app_context():
        p = Project.create_project(

            project_name="sorted-proj",
            description="m-test",
            start_date=_today(),
            
        )

        past_ms = Milestone.create_milestone(
            title="past",
            project_id=p.id,
            due_date=_today(-1),
            status=Milestone.STATUS_NOT_STARTED,
        )
        future_ms = Milestone.create_milestone(
            title="future",
            project_id=p.id,
            due_date=_today(10),
        )

        ordered = p.get_milestones()
        assert ordered[0].id == past_ms.id  # sorted ascending

        active = p.get_active_milestone()
        assert active.id == past_ms.id


def test_update_milestone_progress_propagates(test_app):
    """
    update_milestone_progress should call Milestone.update_completion for
    every milestone – here we stub one milestone to detect the call.
    """
    with test_app.app_context():
        proj = Project.create_project(
            project_name="progress-proj",
            description="",
            start_date=_today(),
        )

        ms = Milestone.create_milestone(
            title="stub",
            project_id=proj.id,
            due_date=_today(1),
        )

        
        called = {"flag": False}

        def _fake_update():
            called["flag"] = True
            return 0.0
        


        ms.update_completion = _fake_update  # type: ignore

        assert proj.update_milestone_progress() is True
        assert called["flag"] is True


 # milestone section
def test_update_completion_no_tasks_not_started(test_app):
    """with no tasks completion → 0 % and status  NOT_STARTED"""
    with test_app.app_context():
        ms = Milestone.create_milestone(
            title="empty-ms",
            project_id=1,

            due_date=_today(),
        )
        pct = ms.update_completion()

        assert pct == 0.0
        assert ms.status == Milestone.STATUS_NOT_STARTED


def test_to_dict_contains_core_fields(test_app):

    with test_app.app_context():
        ms = Milestone.create_milestone(
            title="dict-ms",
            project_id=1,
            due_date=_today(),
        )
        d = ms.to_dict()

        assert {"id", "title", "project_id", "status"} <= d.keys()


def test_create_milestone_invalid_status_falls_back(test_app):
    """passing an invalid status string falls back to   NOT_STARTED."""
    with test_app.app_context():
        ms = Milestone.create_milestone(
            title="bad-status",


            project_id=1,
            due_date=_today(),
            status="made-up",
        )
        
        assert ms.status == Milestone.STATUS_NOT_STARTED

def test_project_milestone_methods(test_app, fresh_user):
    """Test project milestone-related methods."""
    with test_app.app_context():
        project = Project.create_project(
            project_name="Milestone Methods Test",
            description="Testing milestone methods",
            start_date=date.today(),
            created_by_id=fresh_user.id
        )

        # Create multiple milestones
        milestone1 = Milestone.create_milestone(
            title="First Milestone",
            project_id=project.id,
            due_date=date.today() + timedelta(days=5),
            status=Milestone.STATUS_NOT_STARTED
        )

        milestone2 = Milestone.create_milestone(
            title="Second Milestone",
            project_id=project.id,
            due_date=date.today() + timedelta(days=10),
            status=Milestone.STATUS_IN_PROGRESS
        )

        # Test get_milestones
        milestones = project.get_milestones()
        assert len(milestones) == 2
        assert milestone1 in milestones
        assert milestone2 in milestones

        # Test get_active_milestone
        active = project.get_active_milestone()
        assert active is not None
        assert active.status != Milestone.STATUS_COMPLETED

        # Test update_milestone_progress
        result = project.update_milestone_progress()
        assert result is True

def test_project_delete_and_get_all_projects(test_app):
    """Test deleting a project and retrieving all projects."""
    with test_app.app_context():
        proj = Project.create_project(
            project_name="delete-proj",
            description="to be deleted",
            start_date=_today(),
        )
        proj_id = proj.id
        assert proj_id is not None
        # Test get_all_projects
        all_projects = Project.get_all_projects()
        assert any(p.id == proj_id for p in all_projects)
        # Test delete
        proj.delete()
        db.session.commit()
        all_projects = Project.get_all_projects()
        assert not any(p.id == proj_id for p in all_projects)

def test_project_get_files_and_tasks(test_app):
    """Test get_files and get_tasks return lists (empty if no related objects)."""
    with test_app.app_context():
        proj = Project.create_project(
            project_name="files-tasks-proj",
            description="",
            start_date=_today(),
        )
        files = proj.get_files()
        tasks = proj.get_tasks()
        assert isinstance(files, list)
        assert isinstance(tasks, list)

def test_project_get_reports_empty(test_app):
    """Test get_reports returns an empty list if no reports exist."""
    with test_app.app_context():
        proj = Project.create_project(
            project_name="reports-proj",
            description="",
            start_date=_today(),
        )
        reports = proj.get_reports()
        assert isinstance(reports, list)
        assert len(reports) == 0

def test_project_to_dict_exception():
    class BrokenProject:
        def __getattr__(self, name):
            raise Exception('fail')
    p = BrokenProject()
    
    p.id = 123
    p.project_name = 'Fallback'
    result = Project.to_dict(p)
    assert result['id'] == 123 or result['project_name'] == 'Fallback' or 'error' in result

def test_create_project_exception():
    with patch('models.ProjectManagement.project.db.session.add', side_effect=Exception('fail')):
        with pytest.raises(ValueError):
            Project.create_project('fail', '', date.today())

def test_delete_exception(test_app):
    with test_app.app_context():
        proj = Project.create_project('del-exc', '', date.today())
        with patch('models.ProjectManagement.project.db.session.delete', side_effect=Exception('fail')):
            with pytest.raises(ValueError):
                proj.delete()

def test_get_files_exception(test_app):
    with test_app.app_context():
        proj = Project.create_project('files-exc', '', date.today())
        with patch('models.DocumentFileManagement.file.File.query.filter_by', side_effect=Exception('fail')):
            files = proj.get_files()
            assert files == []

def test_get_tasks_exception(test_app):
    with test_app.app_context():
        proj = Project.create_project('tasks-exc', '', date.today())
        with patch('models.TaskManagement.task.Task.query.filter_by', side_effect=Exception('fail')):
            tasks = proj.get_tasks()
            assert tasks == []

def test_get_milestones_exception(test_app):
    with test_app.app_context():
        proj = Project.create_project('ms-exc', '', date.today())
        # Patch the whole Milestone module import to raise Exception
        import sys
        import types
        fake_mod = types.ModuleType('models.ProjectManagement.milestone')
        class FakeMilestone:
            @staticmethod
            def query():
                raise Exception('fail')
        fake_mod.Milestone = FakeMilestone
        sys.modules['models.ProjectManagement.milestone'] = fake_mod
        try:
            with pytest.raises(ValueError):
                proj.get_milestones()
        finally:
            del sys.modules['models.ProjectManagement.milestone']

def test_get_active_milestone_exception(test_app):
    with test_app.app_context():
        proj = Project.create_project('active-ms-exc', '', date.today())
        with patch.object(proj, 'get_milestones', side_effect=Exception('fail')):
            with pytest.raises(ValueError):
                proj.get_active_milestone()

def test_update_milestone_progress_exception(test_app):
    with test_app.app_context():
        proj = Project.create_project('update-ms-exc', '', date.today())
        with patch.object(proj, 'get_milestones', side_effect=Exception('fail')):
            result = proj.update_milestone_progress()
            assert result is False

def test_get_reports_exception(test_app):
    with test_app.app_context():
        proj = Project.create_project('reports-exc', '', date.today())
        with patch('models.AnalysisandReporting.report.Report.query.filter_by', side_effect=Exception('fail')):
            reports = proj.get_reports()
            assert reports == []