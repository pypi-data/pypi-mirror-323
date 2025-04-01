"""This module contains the API routes for managing datasets."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.server.db import get_session
from lightly_purple.server.models import Dataset
from lightly_purple.server.models.dataset import DatasetInput, DatasetView
from lightly_purple.server.resolvers.dataset import DatasetResolver
from lightly_purple.server.routes.api.status import HTTP_STATUS_NOT_FOUND
from lightly_purple.server.routes.api.validators import Paginated

dataset_router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


def get_dataset_resolver(session: SessionDep) -> DatasetResolver:
    """Create an instance of the DatasetResolver."""
    return DatasetResolver(session)


@dataset_router.post(
    "/datasets",
    response_model=DatasetView,
    status_code=201,
)
def create_dataset(
    dataset_input: DatasetInput,
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
) -> Dataset:
    """Create a new dataset in the database."""
    return handler.create(dataset_input)


@dataset_router.get("/datasets")
def read_datasets(
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
    paginated: Annotated[Paginated, Query()],
) -> List[DatasetView]:
    """Retrieve a list of datasets from the database."""
    return handler.get_all(**paginated.model_dump())


@dataset_router.get("/datasets/{dataset_id}")
def read_dataset(
    dataset_id: UUID,
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
) -> Dataset:
    """Retrieve a single dataset from the database."""
    dataset = handler.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Dataset not found"
        )
    return dataset


@dataset_router.put("/datasets/{dataset_id}")
def update_dataset(
    dataset_id: UUID,
    dataset_input: DatasetInput,
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
) -> Dataset:
    """Update an existing dataset in the database."""
    dataset = handler.update(dataset_id, dataset_input)
    if not dataset:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Dataset not found"
        )
    return dataset


@dataset_router.delete("/datasets/{dataset_id}")
def delete_dataset(
    dataset_id: UUID,
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
):
    """Delete a dataset from the database."""
    if not handler.delete(dataset_id):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Dataset not found"
        )
    return {"status": "deleted"}
