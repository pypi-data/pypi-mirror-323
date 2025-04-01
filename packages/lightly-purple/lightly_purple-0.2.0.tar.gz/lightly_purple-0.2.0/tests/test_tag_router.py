from uuid import uuid4

from fastapi.testclient import TestClient

from purple.server.routes.api.dataset_tag import tag_router
from purple.server.routes.api.status import HTTP_STATUS_OK

# Set up the FastAPI TestClient
client = TestClient(tag_router)


def test_read_tags__calls_get_all_by_dataset_id(mocker):
    # Mock the TagResolver
    mock_tag_resolver = mocker.patch(
        "purple.server.routes.api.dataset_tag.TagResolver"
    )

    # Set up the return value for `get_all_by_dataset_id`
    mock_tag_resolver_instance = mock_tag_resolver.return_value
    mock_tag_resolver_instance.get_all_by_dataset_id.return_value = []

    dataset_id = uuid4()
    # Make the request to the `/tags` endpoint
    response = client.get(
        f"/datasets/{dataset_id}/tags", params={"offset": 0, "limit": 100}
    )

    # Assert the response
    assert response.status_code == HTTP_STATUS_OK
    assert response.json() == []

    # Assert that `get_all_by_dataset_id` was called with the correct arguments
    mock_tag_resolver_instance.get_all_by_dataset_id.assert_called_once_with(
        dataset_id=dataset_id, offset=0, limit=100
    )
