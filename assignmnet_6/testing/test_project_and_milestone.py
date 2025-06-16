"""
covers every public method 
"""
from datetime import date, timedelta

import pytest

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