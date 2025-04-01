"""Dataset functionality module."""

import webbrowser
from pathlib import Path
from typing import Optional, Tuple
from uuid import UUID

from labelformat.model.bounding_box import BoundingBoxFormat
from tqdm import tqdm

from purple.dataset.env import APP_URL, PURPLE_HOST, PURPLE_PORT
from purple.server.db import db_manager
from purple.server.models import Dataset
from purple.server.models.annotation import AnnotationInput
from purple.server.models.annotation_label import AnnotationLabelInput
from purple.server.models.dataset import DatasetInput
from purple.server.models.sample import SampleInput
from purple.server.models.tag import TagInput
from purple.server.resolvers.annotation import AnnotationResolver
from purple.server.resolvers.annotation_label import AnnotationLabelResolver
from purple.server.resolvers.dataset import DatasetResolver
from purple.server.resolvers.sample import SampleResolver
from purple.server.resolvers.tag import TagResolver
from purple.server.server import Server

from .yolo_loader import YOLODatasetLoader

# Constants
ANNOTATION_BATCH_SIZE = 64  # Number of annotations to process in a single batch


class DatasetLoader:
    """Class responsible for loading datasets from various sources."""

    def __init__(self):
        """Initialize the dataset loader."""
        self._yolo_loader: Optional[YOLODatasetLoader] = None
        self._dataset: Optional[Dataset] = None
        with db_manager.session() as session:
            self.dataset_resolver = DatasetResolver(session)
            self.tag_resolver = TagResolver(session)
            self.sample_resolver = SampleResolver(session)
            self.annotation_resolver = AnnotationResolver(session)
            self.annotation_label_resolver = AnnotationLabelResolver(session)

    def from_yolo(
        self, data_yaml_path: str, input_split: str = "train"
    ) -> Tuple[YOLODatasetLoader, UUID]:
        """Load a dataset in YOLO format and store in database."""
        if not self._yolo_loader:
            self._yolo_loader = YOLODatasetLoader(data_yaml_path, input_split)

        # Load the dataset
        label_input = self._yolo_loader.load()

        with db_manager.session() as session:  # noqa: F841
            # Create dataset record
            dataset = DatasetInput(
                name=Path(data_yaml_path).parent.name,
                directory=str(Path(data_yaml_path).parent.absolute()),
            )

            self._dataset = self.dataset_resolver.create(dataset)

            # TODO(Kondrat 01/25): We need to expose images_dir from label_input
            img_dir = self._yolo_loader._label_input._images_dir()  # noqa: SLF001

            # Store labels first
            label_map = {}
            for category in tqdm(
                label_input.get_categories(), desc="Processing categories"
            ):
                label = AnnotationLabelInput(
                    annotation_label_name=category.name
                )
                stored_label = self.annotation_label_resolver.create(label)
                label_map[category.id] = stored_label.annotation_label_id

            annotations_to_create = []

            # temporary hack; create dummy tags until we can create tags
            tag_even = self.tag_resolver.create(
                TagInput(dataset_id=self._dataset.dataset_id, name="even")
            )
            tag_mod5 = self.tag_resolver.create(
                TagInput(dataset_id=self._dataset.dataset_id, name="mod5")
            )

            # Process images and annotations
            for i, image_data in enumerate(tqdm(
                label_input.get_labels(), desc="Processing images"
            )):
                # Create sample record
                sample = SampleInput(
                    file_name=str(image_data.image.filename),
                    file_path_abs=str(img_dir / image_data.image.filename),
                    width=image_data.image.width,
                    height=image_data.image.height,
                    dataset_id=self._dataset.dataset_id,
                )
                stored_sample = self.sample_resolver.create(sample)

                # temporary hack; create dummy tags until we can create tags
                if (i % 2) == 0:
                    self.tag_resolver.add_tag_to_sample(
                        tag_even.tag_id, stored_sample
                    )
                if (i % 5) == 0:
                    self.tag_resolver.add_tag_to_sample(
                        tag_mod5.tag_id, stored_sample
                    )

                # Create annotations
                for obj in image_data.objects:
                    box = obj.box.to_format(BoundingBoxFormat.XYWH)
                    x, y, width, height = box

                    annotations_to_create.append(
                        AnnotationInput(
                            dataset_id=self._dataset.dataset_id,
                            sample_id=stored_sample.sample_id,
                            annotation_label_id=label_map[obj.category.id],
                            x=x,
                            y=y,
                            width=width,
                            height=height,
                        )
                    )

                if len(annotations_to_create) >= ANNOTATION_BATCH_SIZE:
                    self.annotation_resolver.create_many(annotations_to_create)
                    annotations_to_create = []

            # Insert any remaining annotations
            if annotations_to_create:
                self.annotation_resolver.create_many(annotations_to_create)
                annotations_to_create = []

        # TODO: we should not return internal state but use getters
        return self._yolo_loader, self._dataset.dataset_id

    def launch(self):
        """Launch the web interface for the loaded dataset."""
        server = Server(host=PURPLE_HOST, port=int(PURPLE_PORT))

        print(f"Opening URL: {APP_URL}")

        # We need to open browser before starting the server
        webbrowser.open_new(APP_URL)

        server.start()
