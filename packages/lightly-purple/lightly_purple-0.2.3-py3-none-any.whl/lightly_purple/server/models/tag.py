"""This module contains the Tag model and related enumerations."""

from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class TagBase(SQLModel):
    """Base class for the Tag model."""

    dataset_id: UUID
    name: str
    description: Optional[str] = None


class TagInput(TagBase):
    """Tag model when creating."""


class TagInputBody(TagInput):
    """Tag model when creating."""

    dataset_id: Optional[UUID] = None  # type: ignore


class TagUpdate(TagBase):
    """Tag model when updating."""


class TagUpdateBody(TagBase):
    """Tag model when updating."""

    dataset_id: Optional[UUID] = None  # type: ignore


class TagView(TagBase):
    """Tag model when retrieving."""

    tag_id: UUID
