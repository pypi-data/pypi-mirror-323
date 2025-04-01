from uuid import uuid4

from fastapi.testclient import TestClient

from purple.server.routes.api.annotation import annotations_router
from purple.server.routes.api.status import HTTP_STATUS_OK

# Set up the FastAPI TestClient
client = TestClient(annotations_router)


def test_read_annotations(mocker):
    # Mock the TagResolver
    mock_annotations_resolver = mocker.patch(
        "purple.server.routes.api.annotation.AnnotationResolver"
    )

    annotations = [
        {
            "x": 1498.0003662109375,
            "y": 315.9999084472656,
            "width": 128.00064086914062,
            "height": 93.99996185302734,
            "sample": {
                "file_path_abs": "/users/beiden/letter-to-mask.png",
                "sample_id": "89715469-3585-4eaf-922b-5f4a7df73a47",
            },
        },
        {
            "x": 251.99952697753906,
            "y": 374.999755859375,
            "width": 22.000320434570312,
            "height": 33.999839782714844,
            "sample": {
                "file_path_abs": "/users/mask/letter-to-trump.png",
                "sample_id": "fbd17aef-d2c9-4b2e-979b-a52098082f8c",
            },
        },
    ]

    # Set up the return value for `get_all`
    mock_tag_resolver_instance = mock_annotations_resolver.return_value
    mock_tag_resolver_instance.get_all.return_value = annotations

    dataset_id = uuid4()

    annotation_label_ids = [uuid4(), uuid4()]
    offset = 10
    # Make the request to the `/tags` endpoint
    response = client.get(
        f"/datasets/{dataset_id}/annotations",
        params={
            "offset": offset,
            "limit": 100,
            "annotation_label_ids": annotation_label_ids,
        },
    )

    # Assert the response
    assert response.status_code == HTTP_STATUS_OK
    assert response.json() == annotations

    # Check `read_annotations` calls the correct resolver method
    mock_tag_resolver_instance.get_all.assert_called_once_with(
        pagination={"offset": offset, "limit": 100},
        filters={
            "dataset_ids": [dataset_id],
            "annotation_label_ids": annotation_label_ids,
            "tag_ids": None,
        },
    )
