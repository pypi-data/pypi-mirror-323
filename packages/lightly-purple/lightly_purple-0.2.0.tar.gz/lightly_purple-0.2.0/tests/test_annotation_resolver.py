import pytest

from tests.helpers_resolvers import (
    create_annotation,
    create_annotation_label,
    create_dataset,
    create_sample,
    create_tag,
)


@pytest.fixture
def test_data(test_resolvers):
    """Fixture that provides test database with sample data."""
    resolver = test_resolvers["annotation"]

    dataset1 = create_dataset(test_resolvers["dataset"])
    dataset1_id = dataset1.dataset_id

    dataset2 = create_dataset(test_resolvers["dataset"])
    dataset2_id = dataset2.dataset_id

    # Create samples
    sample1 = create_sample(test_resolvers["sample"], dataset_id=dataset1_id)
    sample2 = create_sample(test_resolvers["sample"], dataset_id=dataset1_id)

    sample_with_mouse = create_sample(
        test_resolvers["sample"], dataset_id=dataset2_id
    )

    # Create labels
    dog_label = create_annotation_label(
        test_resolvers["label"],
        annotation_label_name="dog",
    )
    cat_label = create_annotation_label(
        test_resolvers["label"],
        annotation_label_name="cat",
    )
    mouse_label = create_annotation_label(
        test_resolvers["label"],
        annotation_label_name="mouse",
    )

    # Create annotations
    dog_annotation1 = create_annotation(
        test_resolvers["annotation"],
        sample_id=sample1.sample_id,
        annotation_label_id=dog_label.annotation_label_id,
        dataset_id=dataset1_id,
    )
    dog_annotation2 = create_annotation(
        test_resolvers["annotation"],
        sample_id=sample2.sample_id,
        annotation_label_id=dog_label.annotation_label_id,
        dataset_id=dataset1_id,
    )
    cat_annotation = create_annotation(
        test_resolvers["annotation"],
        sample_id=sample1.sample_id,
        annotation_label_id=cat_label.annotation_label_id,
        dataset_id=dataset1_id,
    )
    mouse_annoutation = create_annotation(
        test_resolvers["annotation"],
        sample_id=sample_with_mouse.sample_id,
        annotation_label_id=mouse_label.annotation_label_id,
        dataset_id=dataset2_id,
    )

    return {
        "resolver": resolver,
        "dog_label": dog_label,
        "cat_label": cat_label,
        "dog_annotation1": dog_annotation1,
        "dog_annotation2": dog_annotation2,
        "cat_annotation": cat_annotation,
        "dataset": dataset1,
        "sample1": sample1,
        "sample2": sample2,
        "mouse_annoutation": mouse_annoutation,
        "dataset2": dataset2,
        "sample_with_mouse": sample_with_mouse,
    }


def test_create_and_get_annotation(test_data):
    resolver = test_data["resolver"]
    dog_annotation = test_data["dog_annotation1"]

    retrieved_annotation = resolver.get_by_id(dog_annotation.annotation_id)

    assert retrieved_annotation == dog_annotation


def test_count_annotations_labels_by_dataset(test_data):
    resolver = test_data["resolver"]
    dataset = test_data["dataset"]

    annotation_counts = resolver.count_annotations_by_dataset(
        dataset.dataset_id
    )

    assert len(annotation_counts) == 2
    annotation_dict = {
        label: current for (label, current, _) in annotation_counts
    }
    assert annotation_dict["dog"] == 2
    assert annotation_dict["cat"] == 1


def test_count_annotations_by_dataset_with_filtering(test_data):
    resolver = test_data["resolver"]
    dataset = test_data["dataset"]
    dataset_id = dataset.dataset_id

    # Test without filtering
    counts = resolver.count_annotations_by_dataset(dataset_id)
    counts_dict = {label: (current, total) for label, current, total in counts}
    assert counts_dict["dog"] == (
        2,
        2,
    )  # current_count = total_count when no filtering
    assert counts_dict["cat"] == (1, 1)

    # Test with filtering by "dog"
    filtered_counts = resolver.count_annotations_by_dataset(
        dataset_id, filtered_labels=["dog"]
    )
    filtered_dict = {
        label: (current, total) for label, current, total in filtered_counts
    }
    assert filtered_dict["dog"] == (2, 2)  # All dogs are visible
    assert filtered_dict["cat"] == (
        1,
        1,
    )  # Cat from sample1 is visible (because sample1 has a dog)

    # Test with filtering by "cat"
    filtered_counts = resolver.count_annotations_by_dataset(
        dataset_id, filtered_labels=["cat"]
    )
    filtered_dict = {
        label: (current, total) for label, current, total in filtered_counts
    }
    assert filtered_dict["dog"] == (
        1,
        2,
    )  # Only one dog is visible (from sample1)
    assert filtered_dict["cat"] == (1, 1)  # All cats are visible


def test_get_all_with_mulpiple_labels(test_data):
    resolver = test_data["resolver"]
    dog_label = test_data["dog_label"]
    cat_label = test_data["cat_label"]

    annotations = resolver.get_all(
        filters={
            "annotation_label_ids": [
                dog_label.annotation_label_id,
                cat_label.annotation_label_id,
            ]
        }
    )
    assert len(annotations) == 3
    assert all(
        a.annotation_label_id
        in {dog_label.annotation_label_id, cat_label.annotation_label_id}
        for a in annotations
    )


def test_get_all_returns_paginated_results(test_data):
    resolver = test_data["resolver"]

    # Test pagination
    annotations = resolver.get_all(pagination={"offset": 0, "limit": 3})
    assert len(annotations) == 3

    # Test pagination with offset
    annotations = resolver.get_all(pagination={"offset": 3, "limit": 3})
    assert len(annotations) == 1


def test_get_all_returns_filtered_results(test_data):
    resolver = test_data["resolver"]
    dog_label = test_data["dog_label"]

    annotations = resolver.get_all(
        filters={
            "annotation_label_ids": [
                dog_label.annotation_label_id,
            ]
        }
    )

    assert len(annotations) == 2
    assert annotations[0].annotation_label_id == dog_label.annotation_label_id
    assert annotations[1].annotation_label_id == dog_label.annotation_label_id


def test_get_all_returns_filtered_and_paginated_results(test_data):
    resolver = test_data["resolver"]
    dog_label = test_data["dog_label"]
    cat_label = test_data["cat_label"]

    filters = {
        "annotation_label_ids": [
            dog_label.annotation_label_id,
            cat_label.annotation_label_id,
        ]
    }
    annotations = resolver.get_all(
        filters=filters,
        pagination={
            "offset": 0,
            "limit": 2,
        },
    )
    assert len(annotations) == 2

    annotations = resolver.get_all(
        filters=filters,
        pagination={
            "offset": 2,
            "limit": 2,
        },
    )
    assert len(annotations) == 1


def test_get_all_returns_filtered_by_dataset_results(test_data):
    resolver = test_data["resolver"]
    dataset = test_data["dataset"]
    dataset2 = test_data["dataset2"]

    annotations_for_dataset1 = resolver.get_all(
        filters={
            "dataset_ids": [
                dataset.dataset_id,
            ]
        }
    )
    assert len(annotations_for_dataset1) == 3

    annotations_for_dataset2 = resolver.get_all(
        filters={
            "dataset_ids": [
                dataset2.dataset_id,
            ]
        }
    )
    assert len(annotations_for_dataset2) == 1

    annotations_for_both_datasers = resolver.get_all(
        filters={
            "dataset_ids": [
                dataset.dataset_id,
                dataset2.dataset_id,
            ]
        }
    )
    assert len(annotations_for_both_datasers) == 4


def test_add_tag_to_annotation(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    tag = create_tag(test_resolvers["tag"], dataset_id=dataset.dataset_id)
    sample = create_sample(
        test_resolvers["sample"], dataset_id=dataset.dataset_id
    )
    anno_label_cat = create_annotation_label(
        test_resolvers["label"], annotation_label_name="cat"
    )
    annotation = create_annotation(
        test_resolvers["annotation"],
        dataset_id=dataset.dataset_id,
        sample_id=sample.sample_id,
        annotation_label_id=anno_label_cat.annotation_label_id,
    )

    # add annotaiton to tag
    test_resolvers["tag"].add_tag_to_annotation(tag.tag_id, annotation)

    assert annotation.tags.index(tag) == 0


def test_remove_annotation_from_tag(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    tag = create_tag(test_resolvers["tag"], dataset_id=dataset.dataset_id)
    sample = create_sample(
        test_resolvers["sample"], dataset_id=dataset.dataset_id
    )
    anno_label_cat = create_annotation_label(
        test_resolvers["label"], annotation_label_name="cat"
    )
    annotation = create_annotation(
        test_resolvers["annotation"],
        dataset_id=dataset.dataset_id,
        sample_id=sample.sample_id,
        annotation_label_id=anno_label_cat.annotation_label_id,
    )

    # add annotation to tag
    test_resolvers["tag"].add_tag_to_annotation(tag.tag_id, annotation)
    assert len(annotation.tags) == 1
    assert annotation.tags.index(tag) == 0

    # remove annotation to tag
    test_resolvers["tag"].remove_tag_from_annotation(tag.tag_id, annotation)
    assert len(annotation.tags) == 0
    with pytest.raises(ValueError, match="is not in list"):
        annotation.tags.index(tag)


def test_add_and_remove_annotation_ids_to_tag_id(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    tag_1 = create_tag(
        test_resolvers["tag"], dataset_id=dataset.dataset_id, tag_name="tag_all"
    )
    tag_2 = create_tag(
        test_resolvers["tag"], dataset_id=dataset.dataset_id, tag_name="tag_odd"
    )
    sample = create_sample(
        test_resolvers["sample"], dataset_id=dataset.dataset_id
    )
    anno_label_cat = create_annotation_label(
        test_resolvers["label"], annotation_label_name="cat"
    )

    total_annos = 10
    annotations = []
    for _ in range(total_annos):
        annotation = create_annotation(
            test_resolvers["annotation"],
            dataset_id=dataset.dataset_id,
            sample_id=sample.sample_id,
            annotation_label_id=anno_label_cat.annotation_label_id,
        )
        annotations.append(annotation)

    # add all annotations to tag_1
    test_resolvers["tag"].add_annotation_ids_to_tag_id(
        tag_id=tag_1.tag_id,
        annotation_ids=[annotation.annotation_id for annotation in annotations],
    )

    # add every odd annotations to tag_2
    test_resolvers["tag"].add_annotation_ids_to_tag_id(
        tag_id=tag_2.tag_id,
        annotation_ids=[
            annotation.annotation_id
            for i, annotation in enumerate(annotations)
            if i % 2 == 1
        ],
    )

    # ensure all annotations were added to the correct tags
    for i, annotation in enumerate(annotations):
        assert tag_1 in annotation.tags
        if i % 2 == 1:
            assert tag_2 in annotation.tags

    # ensure the correct number of annotations were added to each tag
    assert len(tag_1.annotations) == total_annos
    assert len(tag_2.annotations) == total_annos / 2

    # lets remove every even annotations from tag_1
    # this results in tag_1 and tag_2 having the same annotations
    test_resolvers["tag"].remove_annotation_ids_from_tag_id(
        tag_id=tag_1.tag_id,
        annotation_ids=[
            annotation.annotation_id
            for i, annotation in enumerate(tag_1.annotations)
            if i % 2 == 0
        ],
    )

    assert len(tag_1.annotations) == total_annos / 2
    assert len(tag_2.annotations) == total_annos / 2
    assert tag_1.annotations == tag_2.annotations


def test_get_all__with_tag_filtering(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    tag_1 = create_tag(
        test_resolvers["tag"], dataset_id=dataset.dataset_id, tag_name="tag_all"
    )
    tag_2 = create_tag(
        test_resolvers["tag"], dataset_id=dataset.dataset_id, tag_name="tag_odd"
    )
    sample = create_sample(
        test_resolvers["sample"], dataset_id=dataset.dataset_id
    )
    anno_label_cat = create_annotation_label(
        test_resolvers["label"], annotation_label_name="cat"
    )
    anno_label_dog = create_annotation_label(
        test_resolvers["label"], annotation_label_name="dog"
    )

    total_annos = 10
    annotations = []
    for i in range(total_annos):
        annotation = create_annotation(
            test_resolvers["annotation"],
            dataset_id=dataset.dataset_id,
            sample_id=sample.sample_id,
            annotation_label_id=anno_label_cat.annotation_label_id
            if i < total_annos / 2
            else anno_label_dog.annotation_label_id,
        )
        annotations.append(annotation)

    # add first half to tag_1
    test_resolvers["tag"].add_annotation_ids_to_tag_id(
        tag_id=tag_1.tag_id,
        annotation_ids=[
            annotation.annotation_id
            for _, annotation in enumerate(annotations)
            if annotation.annotation_label_id
            == anno_label_cat.annotation_label_id
        ],
    )

    # add second half to tag_1
    test_resolvers["tag"].add_annotation_ids_to_tag_id(
        tag_id=tag_2.tag_id,
        annotation_ids=[
            annotation.annotation_id
            for _, annotation in enumerate(annotations)
            if annotation.annotation_label_id
            == anno_label_dog.annotation_label_id
        ],
    )

    # Test filtering by tags
    annotations_part1 = test_resolvers["annotation"].get_all(
        filters={"dataset_ids": [dataset.dataset_id], "tag_ids": [tag_1.tag_id]}
    )
    assert len(annotations_part1) == int(total_annos / 2)
    assert all(
        annotation.annotation_label.annotation_label_name == "cat"
        for annotation in annotations_part1
    )

    annotations_part2 = test_resolvers["annotation"].get_all(
        filters={"dataset_ids": [dataset.dataset_id], "tag_ids": [tag_2.tag_id]}
    )
    assert len(annotations_part2) == int(total_annos / 2)
    assert all(
        annotation.annotation_label.annotation_label_name == "dog"
        for annotation in annotations_part2
    )

    # test filtering by both tags
    annotations_all = test_resolvers["annotation"].get_all(
        filters={
            "dataset_id": dataset.dataset_id,
            "tag_ids": [
                tag_1.tag_id,
                tag_2.tag_id,
            ],
        }
    )
    assert len(annotations_all) == total_annos


def test_create_many_annotations(test_resolvers):
    """Test bulk creation of annotations."""
    dataset = create_dataset(test_resolvers["dataset"])
    sample = create_sample(
        test_resolvers["sample"], dataset_id=dataset.dataset_id
    )
    cat_label = create_annotation_label(
        test_resolvers["label"], annotation_label_name="cat"
    )

    annotations_to_create = [
        {
            "sample_id": sample.sample_id,
            "dataset_id": dataset.dataset_id,
            "annotation_label_id": cat_label.annotation_label_id,
            "x": i * 10,
            "y": i * 10,
            "width": 50,
            "height": 50,
        }
        for i in range(3)
    ]

    test_resolvers["annotation"].create_many(annotations_to_create)

    created_annotations = test_resolvers["annotation"].get_all(
        filters={"dataset_ids": [dataset.dataset_id]}
    )

    assert len(created_annotations) == 3
    assert all(
        anno.dataset_id == dataset.dataset_id for anno in created_annotations
    )
    assert all(
        anno.sample_id == sample.sample_id for anno in created_annotations
    )
    assert all(
        anno.annotation_label_id == cat_label.annotation_label_id
        for anno in created_annotations
    )
