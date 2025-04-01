"""Handler for database operations related to datasets."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from lightly_purple.server.models import Dataset
from lightly_purple.server.models.dataset import DatasetInput


class DatasetResolver:
    """Resolver for the Dataset model."""

    def __init__(self, session: Session):  # noqa: D107
        self.session = session

    def create(self, dataset: DatasetInput) -> Dataset:
        """Create a new dataset in the database."""
        db_dataset = Dataset.model_validate(dataset)
        self.session.add(db_dataset)
        self.session.commit()
        self.session.refresh(db_dataset)
        return db_dataset

    def get_all(self, offset: int = 0, limit: int = 100) -> List[Dataset]:
        """Retrieve all datasets with pagination."""
        datasets = self.session.exec(
            select(Dataset).offset(offset).limit(limit)
        ).all()
        return list(datasets) if datasets else []

    def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        """Retrieve a single dataset by ID."""
        return self.session.exec(
            select(Dataset).where(Dataset.dataset_id == dataset_id)
        ).one_or_none()

    def update(
        self, dataset_id: UUID, dataset_data: DatasetInput
    ) -> Optional[Dataset]:
        """Update an existing dataset."""
        dataset = self.get_by_id(dataset_id)
        if not dataset:
            return None

        dataset.name = dataset_data.name
        dataset.directory = dataset_data.directory
        dataset.updated_at = datetime.now(timezone.utc)

        self.session.commit()
        self.session.refresh(dataset)
        return dataset

    def delete(self, dataset_id: UUID) -> bool:
        """Delete a dataset."""
        dataset = self.get_by_id(dataset_id)
        if not dataset:
            return False

        self.session.delete(dataset)
        self.session.commit()
        return True
