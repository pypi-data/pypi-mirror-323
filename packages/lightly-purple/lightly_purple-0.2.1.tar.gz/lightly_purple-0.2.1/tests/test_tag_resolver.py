from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from purple.server.models.tag import TagInput, TagUpdate
from tests.helpers_resolvers import create_dataset, create_tag


def test_create_tag(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag = create_tag(
        test_resolvers["tag"], dataset_id=dataset_id, tag_name="example_tag"
    )
    assert tag.name == "example_tag"


def test_create_tag__unique_tag_name(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_resolver = test_resolvers["tag"]

    create_tag(tag_resolver, dataset_id=dataset_id, tag_name="example_tag")

    # trying to create a tag with the same name results in an IntegrityError
    with pytest.raises(IntegrityError):
        tag_resolver.create(
            TagInput(
                dataset_id=dataset_id,
                name="example_tag",
            )
        )


def test_read_tags(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_resolver = test_resolvers["tag"]

    tag_1 = create_tag(tag_resolver, dataset_id=dataset_id, tag_name="tag_1")
    create_tag(tag_resolver, dataset_id=dataset_id, tag_name="tag_2")
    create_tag(tag_resolver, dataset_id=dataset_id, tag_name="tag_3")

    # get all tags of a dataset
    tags = tag_resolver.get_all_by_dataset_id(dataset_id=dataset_id)
    assert len(tags) == 3
    # check order
    tag = tags[0]
    assert tag.tag_id == tag_1.tag_id
    assert tag.name == tag_1.name


def test_read_tags__paginated(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_resolver = test_resolvers["tag"]

    total = 10
    chunk_size = total / 2
    for i in range(total):
        create_tag(
            tag_resolver, dataset_id=dataset_id, tag_name=f"example_tag_{i}"
        )

    # get first chunk/page
    page_1 = tag_resolver.get_all_by_dataset_id(
        dataset.dataset_id, offset=0, limit=chunk_size
    )
    assert len(page_1) == chunk_size

    # get second chunk/page
    page_2 = tag_resolver.get_all_by_dataset_id(
        dataset.dataset_id, offset=5, limit=chunk_size
    )
    assert len(page_2) == chunk_size

    # assert that the two chunks are different
    assert page_1 != page_2
    assert page_1[0].name != page_2[0].name


def test_read_tag(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_resolver = test_resolvers["tag"]

    tag = create_tag(tag_resolver, dataset_id=dataset_id)

    tag = tag_resolver.get_by_id(tag.tag_id)
    assert tag.tag_id == tag.tag_id
    assert tag.name == "example_tag"


def test_update_tag(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_resolver = test_resolvers["tag"]

    tag = create_tag(tag_resolver, dataset_id=dataset_id)

    data_update = TagUpdate(dataset_id=dataset_id, name="updated_tag")
    tag_updated = tag_resolver.update(tag_id=tag.tag_id, tag_data=data_update)
    # assert tag name changed.
    assert tag_updated.name == data_update.name


def test_update_tag__unique_tag_name(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_resolver = test_resolvers["tag"]

    tag_1 = create_tag(
        tag_resolver, dataset_id=dataset_id, tag_name="example_tag_1"
    )
    tag_2 = create_tag(
        tag_resolver, dataset_id=dataset_id, tag_name="some_other_tag"
    )

    # updating a tag with a name that already exists results in 409
    # trying to create a tag with the same name results in an IntegrityError
    with pytest.raises(IntegrityError):
        tag_resolver.update(
            tag_id=tag_1.tag_id,
            tag_data=TagUpdate(dataset_id=dataset_id, name=tag_2.name),
        )


def test_update_tag__unknown_tag_404(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_resolver = test_resolvers["tag"]

    create_tag(tag_resolver, dataset_id=dataset_id)

    # updating a unknown tag results in 404
    tag_updated = tag_resolver.update(
        tag_id=uuid4(), tag_data={"name": "updated_tag"}
    )
    assert tag_updated is None


def test_delete_tag(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_resolver = test_resolvers["tag"]

    tag = create_tag(tag_resolver, dataset_id=dataset_id)

    # Delete the tag
    tag_resolver.delete(tag.tag_id)

    # assert tag was deleted
    tag_deleted = tag_resolver.get_by_id(tag.tag_id)
    assert tag_deleted is None
