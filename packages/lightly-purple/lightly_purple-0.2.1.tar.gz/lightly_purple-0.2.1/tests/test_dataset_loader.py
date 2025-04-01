import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest
from labelformat.model.bounding_box import BoundingBoxFormat
from sqlmodel import SQLModel, create_engine, select

from purple.dataset.loader import DatasetLoader
from purple.server.db import DatabaseManager
from purple.server.models import Annotation, AnnotationLabel, Dataset, Sample


@pytest.fixture
def db_manager():
    """Create a test database manager."""
    # Create a unique test database file
    db_file = f"{uuid.uuid4().hex}.db"

    # Create a test database manager
    test_manager = DatabaseManager()
    test_manager.engine = create_engine(f"duckdb:///{db_file}")
    SQLModel.metadata.create_all(test_manager.engine)

    yield test_manager

    # Cleanup
    SQLModel.metadata.drop_all(test_manager.engine)


@dataclass
class MockCategory:
    """Mock class for a labelformat.model.category."""

    id: int
    name: str


@dataclass
class MockBox:
    """Mock class for a labelformat.model.bounding_box."""

    x: float
    y: float
    width: float
    height: float

    def to_format(self, format_type):
        """Mock function for a labelformat.model.bounding_box.to_format."""
        if format_type == BoundingBoxFormat.XYWH:
            return [self.x, self.y, self.width, self.height]
        raise ValueError(f"Unknown bbox format: {format_type}")


@dataclass
class MockImage:
    """Mock function for a labelformat.model.image."""

    filename: str = "test_image.jpg"
    width: int = 640
    height: int = 480


@dataclass
class MockSingleObjectDetection:
    """Mock class for a labelformat.model.object_detection."""

    category: MockCategory
    box: MockBox


@dataclass
class MockImageObjectDetection:
    """Mock class for a labelformat.model.object_detection."""

    image: MockImage
    objects: list


class MockYOLOv8ObjectDetectionInput:
    """Mock class for a labelformat.formats.yolov8."""

    def __init__(self):  # noqa: D107
        self.categories = [MockCategory(0, "person"), MockCategory(1, "car")]

    def get_labels(self):  # noqa: D102
        image = MockImage()
        objects = [
            MockSingleObjectDetection(
                self.categories[0], MockBox(0.5, 0.5, 0.2, 0.3)
            )
        ]
        return [MockImageObjectDetection(image, objects)]

    def get_categories(self):  # noqa: D102
        return self.categories


@pytest.fixture
def mock_yolo_v8_data():
    return MockYOLOv8ObjectDetectionInput()


def test_from_yolo(db_manager, mock_yolo_v8_data):
    # Arrange
    data_yaml_path = "/fake/path/data.yaml"

    # Mock the database manager in the loader module
    with patch("purple.dataset.loader.db_manager", db_manager):
        loader = DatasetLoader()

        # Mock the YOLODatasetLoader
        with patch(
            "purple.dataset.loader.YOLODatasetLoader"
        ) as mock_yolo_loader:
            mock_yolo_loader_instance = mock_yolo_loader.return_value
            mock_yolo_loader_instance.load.return_value = mock_yolo_v8_data

            # Act
            loader.from_yolo(data_yaml_path)

            # Assert
            with db_manager.session() as session:
                # Check if dataset was created
                dataset: Dataset = session.exec(select(Dataset)).first()
                assert dataset is not None
                assert dataset.name == Path(data_yaml_path).parent.name

                # Check if labels were created
                labels: List[AnnotationLabel] = session.exec(
                    select(AnnotationLabel)
                ).all()
                assert len(labels) == 2
                assert labels[0].annotation_label_name == "person"
                assert labels[1].annotation_label_name == "car"

                # Check if sample was created
                sample: Sample = session.exec(select(Sample)).first()
                assert sample is not None
                assert sample.file_name == "test_image.jpg"
                assert sample.width == 640
                assert sample.height == 480

                # Check if annotation was created
                annotation: Annotation = session.exec(
                    select(Annotation)
                ).first()
                assert annotation is not None
                assert annotation.x == pytest.approx(0.5)
                assert annotation.x == pytest.approx(0.5)
                assert annotation.width == pytest.approx(0.2)
                assert annotation.height == pytest.approx(0.3)


# This test does not make sense with the code; the loader creates a new dataset
# every time from_yolo is called. This test only checks that a stored datasetId
# of the loader stays the same for multiple calls.
# Additionally a YOLODatasetLoader instance cant be reused anyway because
# the instance holds the path to the data.yaml file
def skip__test_from_yolo_multiple_calls(db_manager, mock_yolo_v8_data):
    # Test that multiple calls reuse the same YOLODatasetLoader instance
    with patch("purple.dataset.loader.db_manager", db_manager):
        loader = DatasetLoader()

        with patch(
            "purple.dataset.loader.YOLODatasetLoader"
        ) as mock_yolo_loader:
            mock_yolo_loader_instance = mock_yolo_loader.return_value
            mock_yolo_loader_instance.load.return_value = mock_yolo_v8_data

            loader.from_yolo("path1/data.yaml")
            loader.from_yolo("path2/data.yaml")

            # YOLODatasetLoader should only be instantiated once
            assert mock_yolo_loader.call_count == 1

            first_result, id1 = loader.from_yolo("path1/data.yaml")
            second_result, id2 = loader.from_yolo("path2/data.yaml")
            assert id1 is id2


def skip__test_from_dataset_id(db_manager, mock_yolo_v8_data):
    # Arrange
    data_yaml_path = "/fake/path/data.yaml"

    # Mock the database manager in the loader module
    with patch("purple.dataset.loader.db_manager", db_manager):
        dataset_id = None
        loader_1 = DatasetLoader()

        # Mock the YOLODatasetLoader
        with patch(
            "purple.dataset.loader.YOLODatasetLoader"
        ) as mock_yolo_loader:
            mock_yolo_loader_instance = mock_yolo_loader.return_value
            mock_yolo_loader_instance.load.return_value = mock_yolo_v8_data

            # Act
            _, dataset_id = loader_1.from_yolo(data_yaml_path)

        # load the previously created dataset again
        loader2 = DatasetLoader()
        loader2.from_dataset_id(dataset_id.hex)

        # Assert that the dataset was loaded
        with db_manager.session() as session:
            # Check that only one dataset was created
            datasets: List[Dataset] = session.exec(select(Dataset)).all()
            assert len(datasets) == 1

            dataset: Dataset = session.exec(
                select(Dataset).where(Dataset.dataset_id == dataset_id)
            ).one_or_none()
            assert dataset is not None
