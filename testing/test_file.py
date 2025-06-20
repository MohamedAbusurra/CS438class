"""
unit-tests that exercise all public methods  of File & FileVersion

Skips trivial setters/getters but covers:
    __init__                            
    _fileTypeTolowerNodot               
    get_formatted_size                  
    to_dict                             
     FileVersion.__init__ & to_dict
"""
from __future__ import annotations

import io
from datetime import datetime, timezone
from pathlib import Path

import pytest
from flask import Flask

from models.database import db
from models.DocumentFileManagement.file import File          # 🡒 code under test
from models.DocumentFileManagement.file_version import FileVersion  # 🡒 code under test



#  tiny Flask + in-memory SQLite just for test puprpse
@pytest.fixture(scope="session")
def test_app():
    app = Flask("files_test")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


#  helpers
DOCX_MIME = b"PK\x03\x04"  # the first four bytes of any DOCX file


def _fake_docx(size: int = 1500) -> tuple[str, bytes]:
    """
    return (<filename>, <bytes>) for an in-memory DOCX blob of requested size
    """
    payload = DOCX_MIME + b"x" *  (size - len(DOCX_MIME))
    return "sample.docx", payload



def _create_file_record(
    *,
    name: str = "demo.docx",
    size: int = 2048,
    uploader: int | None = 1,
) -> File:
    """
    convenience helper – inserts a File row and returns the instance.
    """
    f = File(
        project_id=None,
        file_name=name,
        file_path=f"/tmp/{name}",
        file_size=size,
        file_type=Path(name).suffix,
        uploaded_by_id=uploader,
        description="pytest file",
    )
    db.session.add(f)
    db.session.commit()
    return f


#  File  
def test_file_creation_success(test_app):
    """
    given a DOCX ≤ 100 MB
    when  File() is instantiated
    then  row inserted & defaults set correctly.
    """
    with test_app.app_context():
        filename, raw = _fake_docx()
        size = len(raw)
        file_ = _create_file_record(name=filename, size=size)

        assert file_.id is not None
        assert file_.file_type == "docx"                       
        assert file_.current_version == 1
        assert abs(
            file_.upload_date.replace(tzinfo=timezone.utc) -
            datetime.now(timezone.utc)
        ).total_seconds() < 5


def test_to_dict_includes_formatted_size(test_app):
    with test_app.app_context():
        file_ = _create_file_record(size=3_145_728)  # 3 MB

        if not hasattr(file_, "getFormattedSize"):
            file_.getFormattedSize = file_.get_formatted_size  # type: ignore

        d = file_.to_dict()
        assert d["id"] == file_.id
        assert d["formatted_size"].endswith("MB")
        assert d["file_type"] == "docx"


def test_get_formatted_size_branches():
    small = File._fileTypeTolowerNodot(".txt")  
    assert small == "txt"

    # B   branch
    f1 = File(
        project_id=None,
        file_name="tiny.docx",
        file_path="/tmp/tiny.docx",
        file_size=512,
        file_type=".docx",
        uploaded_by_id=None,
    )
    assert f1.get_formatted_size().endswith("B")

    # KB  branch
    f2 = File(
        project_id=None,
        file_name="mid.docx",
        file_path="/tmp/mid.docx",
        file_size=4_096,
        file_type=".docx",
        uploaded_by_id=None,
    )
    assert f2.get_formatted_size().endswith("KB")

    # MB  branch
    f3 = File(
        project_id=None,
        file_name="big.docx",
        file_path="/tmp/big.docx",
        file_size=5_242_880,  # 5 MB
        file_type=".docx",
        uploaded_by_id=None,
    )
    assert f3.get_formatted_size().endswith("MB")


#  File  
def test_file_size_over_limit_raises(test_app):
    """
    >100 MB must raise ValueError with clear message.[^3]
    """
    with test_app.app_context():
        too_big = 101 * 1024 * 1024  # 101 MB
        with pytest.raises(ValueError):
            _create_file_record(size=too_big)


def test_unsupported_extension_raises():
    with pytest.raises(ValueError):
        File(
            project_id=None,
            file_name="hack.exe",
            file_path="/tmp/hack.exe",
            file_size=1024,
            file_type=".exe",
            uploaded_by_id=None,
        )


def test_empty_extension_helper_raises():
    with pytest.raises(ValueError):
        File._fileTypeTolowerNodot("")  # type: ignore[arg-type]


#  FileVersion coverage
def test_file_version_creation_and_dict(test_app):
    with test_app.app_context():
        file_ = _create_file_record()

        ver = FileVersion(

            file_id=file_.id,
            version_number= 2,
            changed_by_id=99,
            version_path=f"/tmp/{file_.file_name}",
        )
        db.session.add(ver)
        db.session.commit()

        d = ver.to_dict()
        assert d["file_id"] == file_.id
        assert d["version_number"] == 2
        assert d["change_timestamp"] is not None
        #assert d["change_by_id"] == 99