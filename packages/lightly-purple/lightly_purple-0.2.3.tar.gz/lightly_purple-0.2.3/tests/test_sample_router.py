from typing import Mapping
from uuid import uuid4

from fastapi.testclient import TestClient

from lightly_purple.server.models import SampleView
from lightly_purple.server.routes.api.sample import samples_router
from lightly_purple.server.routes.api.status import HTTP_STATUS_CREATED, HTTP_STATUS_OK

# Set up the FastAPI TestClient
client = TestClient(samples_router)


def test_read_samples_calls_get_all(mocker):
    # Mock the SampleResolver
    mock_sample_resolver = mocker.patch(
        "purple.server.routes.api.sample.SampleResolver"
    )
    uuid = uuid4()

    # Set up the return value for `get_all`
    mock_sample_resolver_instance = mock_sample_resolver.return_value
    mock_sample_resolver_instance.get_all_by_dataset_id.return_value = []

    # Make the request to the `/samples` endpoint
    params: Mapping = {
        "dataset_id": uuid,
        "min_width": 10,
        "max_width": 100,
        "min_height": 10,
        "max_height": 100,
        "annotation_labels": ["label1", "label2"],
        "tag_ids": [uuid4(), uuid4(), uuid4()],
        "offset": 0,
        "limit": 100,
    }
    response = client.get("/samples", params=params)

    # Assert the response
    assert response.status_code == HTTP_STATUS_OK
    assert (
        response.json() == []
    )  # Empty list as per mocked `get_all_by_dataset_id` return value

    # Assert that `get_all_by_dataset_id` was called with the correct arguments
    mock_sample_resolver_instance.get_all_by_dataset_id.assert_called_once_with(
        **dict(params)
    )


def test_get_samples_dimensions_calls_get_dimension_bounds(mocker):
    # Mock the SampleResolver
    mock_sample_resolver = mocker.patch(
        "purple.server.routes.api.sample.SampleResolver"
    )
    uuid = uuid4()

    # Set up the return value for `get_dimension_bounds`
    mock_sample_resolver_instance = mock_sample_resolver.return_value
    mock_sample_resolver_instance.get_dimension_bounds.return_value = {
        "min_width": 0,
        "max_width": 100,
        "min_height": 0,
        "max_height": 100,
    }

    # Make the request to the `/samples/dimensions` endpoint
    response = client.get(f"/samples/dimensions?dataset_id={uuid}")

    # Assert the response
    assert response.status_code == HTTP_STATUS_OK
    assert response.json() == {
        "min_width": 0,
        "max_width": 100,
        "min_height": 0,
        "max_height": 100,
    }

    # Assert that `get_dimension_bounds` was called with the correct arguments
    mock_sample_resolver_instance.get_dimension_bounds.assert_called_once_with(
        uuid, annotation_labels=None
    )


def test_add_tag_to_sample_calls_add_tag_to_sample(mocker):
    # Mock the SampleResolver
    mock_sample_resolver = mocker.patch(
        "purple.server.routes.api.sample.SampleResolver"
    )
    mock_tag_resolver = mocker.patch(
        "purple.server.routes.api.dataset_tag.TagResolver"
    )

    tag_id = uuid4()
    sample_id = uuid4()

    sample = SampleView(
        sample_id=sample_id,
        file_path_abs="/path/to/sample1.png",
        file_name="sample1.jpg",
    )

    # Set up the return value for `get_by_id`
    mock_sample_resolver_instance = mock_sample_resolver.return_value
    mock_sample_resolver_instance.get_by_id.return_value = sample

    # set up the return value for `add_tag_to_sample`
    mock_tag_resolver_instance = mock_tag_resolver.return_value
    mock_tag_resolver_instance.add_tag_to_sample.return_value = True

    # Make the request to add sample to a tag
    response = client.post(f"/samples/{sample_id}/tag/{tag_id}")

    # Assert the response
    assert response.status_code == HTTP_STATUS_CREATED

    # Assert that `add_tag_to_sample` was called with the correct arguments
    mock_tag_resolver_instance.add_tag_to_sample.assert_called_once_with(
        tag_id,
        sample,
    )


def test_remove_tag_from_sample_calls_remove_tag_from_sample(mocker):
    # Mock the SampleResolver
    mock_sample_resolver = mocker.patch(
        "purple.server.routes.api.sample.SampleResolver"
    )
    mock_tag_resolver = mocker.patch(
        "purple.server.routes.api.dataset_tag.TagResolver"
    )

    tag_id = uuid4()
    sample_id = uuid4()

    sample = SampleView(
        sample_id=sample_id,
        file_path_abs="/path/to/sample1.png",
        file_name="sample1.jpg",
    )

    # Set up the return value for `get_by_id`
    mock_sample_resolver_instance = mock_sample_resolver.return_value
    mock_sample_resolver_instance.get_by_id.return_value = sample

    # set up the return value for `remove_tag_from_sample`
    mock_tag_resolver_instance = mock_tag_resolver.return_value
    mock_tag_resolver_instance.remove_tag_from_sample.return_value = True

    # Make the request to add sample to a tag
    response = client.delete(f"/samples/{sample_id}/tag/{tag_id}")

    # Assert the response
    assert response.status_code == HTTP_STATUS_OK

    # Assert that `remove_tag_from_sample` was called with the correct arguments
    mock_tag_resolver_instance.remove_tag_from_sample.assert_called_once_with(
        tag_id,
        sample,
    )
