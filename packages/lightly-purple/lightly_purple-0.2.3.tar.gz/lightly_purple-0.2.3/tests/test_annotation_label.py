import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from lightly_purple.server.app import app
from lightly_purple.server.db import get_session
from lightly_purple.server.routes.api.status import (
    HTTP_STATUS_CREATED,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_OK,
)


@pytest.fixture
def test_client():
    db_file = f"{uuid.uuid4().hex}.db"
    engine = create_engine(f"duckdb:///{db_file}")
    SQLModel.metadata.create_all(engine)

    client = TestClient(app)

    with Session(engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        yield client  # This will be used in the test

        app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(engine)  # Optional: Clean up after tests

    if os.path.exists(db_file):
        os.remove(db_file)


def create_annotation_label(client):
    """Helper function to create an annotation label and return its ID."""
    input_label = {
        "annotation_label_id": None,
        "annotation_label_name": "Test Label",
    }
    new_label_result = client.post(
        "/api/annotation_labels",
        json=input_label,
    )
    assert new_label_result.status_code == HTTP_STATUS_CREATED
    return new_label_result.json()["annotation_label_id"], input_label


def test_create_annotation_label(test_client):
    client = test_client
    label_id, input_label = create_annotation_label(client)

    # Validate the created annotation label
    assert label_id is not None
    assert input_label["annotation_label_name"] == "Test Label"


def test_get_annotation_labels(test_client):
    client = test_client
    create_annotation_label(client)

    labels_result = client.get("/api/annotation_labels")
    assert labels_result.status_code == HTTP_STATUS_OK

    label = labels_result.json()[0]
    assert label["annotation_label_name"] == "Test Label"


def test_get_annotation_label(test_client):
    client = test_client
    label_id, input_label = create_annotation_label(client)

    label_result = client.get(f"/api/annotation_labels/{label_id}")
    assert label_result.status_code == HTTP_STATUS_OK

    label = label_result.json()
    assert (
        label["annotation_label_name"] == input_label["annotation_label_name"]
    )


def test_update_annotation_label(test_client):
    client = test_client
    label_id, input_label = create_annotation_label(client)

    updated_label = {
        "annotation_label_id": label_id,
        "annotation_label_name": "Updated Label",
    }

    label_result = client.put(
        f"/api/annotation_labels/{label_id}", json=updated_label
    )
    assert label_result.status_code == HTTP_STATUS_OK

    label = label_result.json()
    assert (
        label["annotation_label_name"] == updated_label["annotation_label_name"]
    )


def test_delete_annotation_label(test_client):
    client = test_client
    label_id, _ = create_annotation_label(client)

    label_result = client.delete(f"/api/annotation_labels/{label_id}")
    assert label_result.status_code == HTTP_STATUS_OK
    assert label_result.json() == {"status": "deleted"}

    label_result = client.get(f"/api/annotation_labels/{label_id}")
    assert label_result.status_code == HTTP_STATUS_NOT_FOUND
