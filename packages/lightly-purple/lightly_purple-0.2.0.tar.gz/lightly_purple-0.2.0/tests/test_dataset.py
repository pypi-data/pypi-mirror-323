import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from purple.server.app import app
from purple.server.db import get_session
from purple.server.routes.api.status import (
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_CREATED,
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_OK,
    HTTP_STATUS_UNPRECESSABLE_ENTITY,
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

        yield client

        app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(engine)

    if os.path.exists(db_file):
        os.remove(db_file)


def create_dataset(
    client, name="example_dataset", directory="/path/to/dataset"
):
    """Helper function to create a dataset and return its ID."""
    dataset_data = {
        "name": name,
        "directory": directory,
    }
    response = client.post("/api/datasets", json=dataset_data)
    assert (
        response.status_code == HTTP_STATUS_CREATED
    ), f"Dataset creation failed: {response.json()}"
    return response.json()["dataset_id"]


def test_create_dataset(test_client):
    client = test_client
    dataset_id = create_dataset(client)

    # Validate the created dataset
    response = client.get(f"/api/datasets/{dataset_id}")
    assert response.status_code == HTTP_STATUS_OK
    dataset = response.json()
    assert dataset["name"] == "example_dataset"
    assert dataset["directory"] == "/path/to/dataset"


def test_create_dataset__invalid_data(test_client):
    client = test_client
    # Attempt to create a dataset with invalid data (missing required fields)
    invalid_data = {
        "name": "example_dataset",
        # Missing required directory field
    }
    response = client.post("/api/datasets", json=invalid_data)
    assert response.status_code == HTTP_STATUS_UNPRECESSABLE_ENTITY


@pytest.mark.skip("A dataset should be named uniquely")
def test_create_dataset__duplicate_name(test_client):
    client = test_client
    dataset_data = {"name": "example_dataset", "directory": "somewhere"}
    response = client.post("/api/datasets", json=dataset_data)
    assert response.status_code == HTTP_STATUS_CREATED

    # Attempt to create a dataset with already existing name conflicts
    response = client.post("/api/datasets", json=dataset_data)
    assert response.status_code == HTTP_STATUS_CONFLICT


def test_read_datasets(test_client):
    client = test_client
    dataset_id = create_dataset(client)

    response = client.get("/api/datasets")
    assert response.status_code == HTTP_STATUS_OK

    datasets = response.json()
    assert len(datasets) == 1
    dataset = datasets[0]
    assert dataset["dataset_id"] == dataset_id
    assert dataset["name"] == "example_dataset"
    assert dataset["directory"] == "/path/to/dataset"


def test_read_dataset(test_client):
    client = test_client
    dataset_id = create_dataset(client)

    response = client.get(f"/api/datasets/{dataset_id}")
    assert response.status_code == HTTP_STATUS_OK

    dataset = response.json()
    assert dataset["dataset_id"] == dataset_id
    assert dataset["name"] == "example_dataset"
    assert dataset["directory"] == "/path/to/dataset"


def test_update_dataset(test_client):
    client = test_client
    dataset_id = create_dataset(client)

    # Update the dataset
    updated_data = {
        "name": "updated_dataset",
        "directory": "/updated/path",
    }

    response = client.put(f"/api/datasets/{dataset_id}", json=updated_data)
    assert response.status_code == HTTP_STATUS_OK

    dataset = response.json()
    assert dataset["name"] == "updated_dataset"
    assert dataset["directory"] == "/updated/path"


def test_delete_dataset(test_client):
    client = test_client
    dataset_id = create_dataset(client)

    # Delete the dataset
    response = client.delete(f"/api/datasets/{dataset_id}")
    assert response.status_code == HTTP_STATUS_OK
    assert response.json() == {"status": "deleted"}

    # Verify the dataset is deleted
    response = client.get(f"/api/datasets/{dataset_id}")
    assert response.status_code == HTTP_STATUS_NOT_FOUND
