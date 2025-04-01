import pytest

from lightly_purple.server.models.sample import SampleInput
from lightly_purple.server.resolvers.annotation import (
    AnnotationInput,
)
from lightly_purple.server.resolvers.annotation_label import (
    AnnotationLabelInput,
)
from tests.helpers_resolvers import create_dataset, create_sample, create_tag


def test_get_all_by_dataset_id(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    resolver = test_resolvers["sample"]

    # create samples
    create_sample(
        resolver, dataset_id=dataset_id, file_path_abs="/path/to/sample1.png"
    )
    create_sample(
        resolver, dataset_id=dataset_id, file_path_abs="/path/to/sample2.png"
    )

    # Act
    samples = resolver.get_all_by_dataset_id(dataset_id=dataset_id)

    # Assert
    assert len(samples) == 2
    assert samples[0].file_name == "sample1.png"
    assert samples[1].file_name == "sample2.png"


def test_get_all_by_dataset_id__with_pagination(test_resolvers):
    # Arrange
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    resolver = test_resolvers["sample"]

    # Create sample data with known sample_ids to ensure consistent ordering
    samples = []
    for i in range(5):  # Create 5 samples
        sample = create_sample(
            resolver,
            dataset_id=dataset_id,
            file_path_abs=f"/sample{i}.png",
            width=100 + i,
            height=100 + i,
        )
        samples.append(sample)

    # Sort samples by sample_id to match the expected order
    samples.sort(key=lambda x: x.file_name)

    # Act - Get first 2 samples
    samples_page_1 = resolver.get_all_by_dataset_id(
        dataset_id=dataset_id, offset=0, limit=2
    )
    # Act - Get next 2 samples
    samples_page_2 = resolver.get_all_by_dataset_id(
        dataset_id=dataset_id, offset=2, limit=2
    )
    # Act - Get remaining samples
    samples_page_3 = resolver.get_all_by_dataset_id(
        dataset_id=dataset_id, offset=4, limit=2
    )

    # Assert - Check first page
    assert len(samples_page_1) == 2
    assert samples_page_1[0].file_name == samples[0].file_name
    assert samples_page_1[1].file_name == samples[1].file_name

    # Assert - Check second page
    assert len(samples_page_2) == 2
    assert samples_page_2[0].file_name == samples[2].file_name
    assert samples_page_2[1].file_name == samples[3].file_name

    # Assert - Check third page (should return 1 sample)
    assert len(samples_page_3) == 1
    assert samples_page_3[0].file_name == samples[4].file_name

    # Assert - Check out of bounds (should return empty list)
    samples_empty = resolver.get_all_by_dataset_id(
        dataset_id=dataset_id, offset=5, limit=2
    )
    assert len(samples_empty) == 0


def test_get_all_by_dataset_id__empty_output(test_resolvers):
    # Arrange
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    resolver = test_resolvers["sample"]

    # Act
    samples = resolver.get_all_by_dataset_id(dataset_id=dataset_id)

    # Assert
    assert len(samples) == 0  # Should return an empty list


def test_get_all_by_dataset_id__with_annotation_filtering(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id

    # Create samples
    sample1 = test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="sample1.png",
            width=100,
            height=100,
        )
    )
    sample2 = test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="sample2.png",
            width=200,
            height=200,
        )
    )

    # Create labels
    dog_label = test_resolvers["label"].create(
        AnnotationLabelInput(dataset_id=dataset_id, annotation_label_name="dog")
    )
    cat_label = test_resolvers["label"].create(
        AnnotationLabelInput(dataset_id=dataset_id, annotation_label_name="cat")
    )

    # Add annotations: sample1 has dog, sample2 has cat
    test_resolvers["annotation"].create(
        AnnotationInput(
            sample_id=sample1.sample_id,
            annotation_label_id=dog_label.annotation_label_id,
            dataset_id=dataset_id,
            x=50,
            y=50,
            width=20,
            height=20,
        )
    )
    test_resolvers["annotation"].create(
        AnnotationInput(
            sample_id=sample2.sample_id,
            annotation_label_id=cat_label.annotation_label_id,
            dataset_id=dataset_id,
            x=70,
            y=70,
            width=30,
            height=30,
        )
    )

    # Test without filtering
    samples = test_resolvers["sample"].get_all_by_dataset_id(dataset_id)
    assert len(samples) == 2

    # Test filtering by dog
    dog_samples = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id, annotation_labels=["dog"]
    )
    assert len(dog_samples) == 1
    assert dog_samples[0].file_name == "sample1.png"

    # Test filtering by cat
    cat_samples = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id, annotation_labels=["cat"]
    )
    assert len(cat_samples) == 1
    assert cat_samples[0].file_name == "sample2.png"

    # Test filtering by both
    all_samples = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id, annotation_labels=["dog", "cat"]
    )
    assert len(all_samples) == 2


def test_get_dimension_bounds(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id

    # Create samples with different dimensions
    test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="small.jpg",
            width=100,
            height=200,
        )
    )
    test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="large.jpg",
            width=1920,
            height=1080,
        )
    )

    bounds = test_resolvers["sample"].get_dimension_bounds(dataset_id)
    assert bounds["min_width"] == 100
    assert bounds["max_width"] == 1920
    assert bounds["min_height"] == 200
    assert bounds["max_height"] == 1080


def test_get_all_by_dataset_id__with_dimension_filtering(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id

    # Create samples with different dimensions
    test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="small.jpg",
            width=100,
            height=200,
        )
    )
    test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="medium.jpg",
            width=800,
            height=600,
        )
    )
    test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="large.jpg",
            width=1920,
            height=1080,
        )
    )

    # Test width filtering
    samples = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id, min_width=500
    )
    assert len(samples) == 2
    assert all(s.width >= 500 for s in samples)

    # Test height filtering
    samples = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id, max_height=700
    )
    assert len(samples) == 2
    assert all(s.height <= 700 for s in samples)

    # Test combined filtering
    samples = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id, min_width=500, max_width=1000, min_height=500
    )
    assert len(samples) == 1
    assert samples[0].file_name == "medium.jpg"


def test_get_dimension_bounds__with_tag_filtering(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id

    # Create samples with different dimensions
    sample1 = test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/small.png",
            file_name="small.jpg",
            width=100,
            height=200,
        )
    )
    sample2 = test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/medium.png",
            file_name="medium.jpg",
            width=800,
            height=600,
        )
    )
    sample3 = test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/large.png",
            file_name="large.jpg",
            width=1920,
            height=1080,
        )
    )

    # create tag of medium->large images
    tag_bigger = create_tag(
        test_resolvers["tag"], dataset.dataset_id, tag_name="bigger"
    )
    test_resolvers["tag"].add_sample_ids_to_tag_id(
        tag_id=tag_bigger.tag_id,
        sample_ids=[sample2.sample_id, sample3.sample_id],
    )

    # create tag of medium->small images
    tag_smaller = create_tag(
        test_resolvers["tag"], dataset.dataset_id, tag_name="smaller"
    )
    test_resolvers["tag"].add_sample_ids_to_tag_id(
        tag_id=tag_smaller.tag_id,
        sample_ids=[sample1.sample_id, sample2.sample_id],
    )

    # Test width filtering of bigger samples
    bounds = test_resolvers["sample"].get_dimension_bounds(
        dataset_id=dataset_id, tag_ids=[tag_bigger.tag_id]
    )
    assert bounds["min_width"] == 800
    assert bounds["max_width"] == 1920
    assert bounds["min_height"] == 600
    assert bounds["max_height"] == 1080

    # Test height filtering of smaller samples
    bounds = test_resolvers["sample"].get_dimension_bounds(
        dataset_id=dataset_id, tag_ids=[tag_smaller.tag_id]
    )
    assert bounds["min_width"] == 100
    assert bounds["max_width"] == 800
    assert bounds["min_height"] == 200
    assert bounds["max_height"] == 600


def test_get_dimension_bounds_with_annotation_filtering(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id

    # Create samples with different dimensions
    sample1 = test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="small.jpg",
            width=100,
            height=200,
        )
    )
    sample2 = test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="medium.jpg",
            width=500,
            height=600,
        )
    )
    sample3 = test_resolvers["sample"].create(
        SampleInput(
            dataset_id=dataset_id,
            file_path_abs="/path/to/sample1.png",
            file_name="large.jpg",
            width=1920,
            height=1080,
        )
    )

    # Create labels
    dog_label = test_resolvers["label"].create(
        AnnotationLabelInput(dataset_id=dataset_id, annotation_label_name="dog")
    )
    cat_label = test_resolvers["label"].create(
        AnnotationLabelInput(dataset_id=dataset_id, annotation_label_name="cat")
    )

    # Add annotations:
    # - small image has dog
    # - medium image has both dog and cat
    # - large image has cat
    test_resolvers["annotation"].create(
        AnnotationInput(
            sample_id=sample1.sample_id,
            annotation_label_id=dog_label.annotation_label_id,
            dataset_id=dataset_id,
            x=50,
            y=50,
            width=20,
            height=20,
        )
    )
    test_resolvers["annotation"].create(
        AnnotationInput(
            sample_id=sample2.sample_id,
            annotation_label_id=dog_label.annotation_label_id,
            dataset_id=dataset_id,
            x=250,
            y=300,
            width=30,
            height=30,
        )
    )
    test_resolvers["annotation"].create(
        AnnotationInput(
            sample_id=sample2.sample_id,
            annotation_label_id=cat_label.annotation_label_id,
            dataset_id=dataset_id,
            x=250,
            y=300,
            width=40,
            height=40,
        )
    )
    test_resolvers["annotation"].create(
        AnnotationInput(
            sample_id=sample3.sample_id,
            annotation_label_id=cat_label.annotation_label_id,
            dataset_id=dataset_id,
            x=960,
            y=540,
            width=100,
            height=100,
        )
    )

    # Test without filtering (should get all samples)
    bounds = test_resolvers["sample"].get_dimension_bounds(dataset_id)
    assert bounds["min_width"] == 100
    assert bounds["max_width"] == 1920
    assert bounds["min_height"] == 200
    assert bounds["max_height"] == 1080

    # Test filtering by dog (should only get small and medium images)
    dog_bounds = test_resolvers["sample"].get_dimension_bounds(
        dataset_id, annotation_labels=["dog"]
    )
    assert dog_bounds["min_width"] == 100
    assert dog_bounds["max_width"] == 500
    assert dog_bounds["min_height"] == 200
    assert dog_bounds["max_height"] == 600

    # Test filtering by cat (should only get medium and large images)
    cat_bounds = test_resolvers["sample"].get_dimension_bounds(
        dataset_id, annotation_labels=["cat"]
    )
    assert cat_bounds["min_width"] == 500
    assert cat_bounds["max_width"] == 1920
    assert cat_bounds["min_height"] == 600
    assert cat_bounds["max_height"] == 1080

    # Test filtering by both dog and cat (should only get medium image)
    both_bounds = test_resolvers["sample"].get_dimension_bounds(
        dataset_id, annotation_labels=["dog", "cat"]
    )
    assert both_bounds["min_width"] == 500
    assert both_bounds["max_width"] == 500
    assert both_bounds["min_height"] == 600
    assert both_bounds["max_height"] == 600


def test_add_tag_to_sample(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag = create_tag(test_resolvers["tag"], dataset_id=dataset_id)
    sample = create_sample(test_resolvers["sample"], dataset_id=dataset_id)

    # add sample to tag
    test_resolvers["tag"].add_tag_to_sample(tag.tag_id, sample)

    assert sample.tags.index(tag) == 0


def test_remove_sample_from_tag(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag = create_tag(test_resolvers["tag"], dataset_id=dataset_id)
    sample = create_sample(test_resolvers["sample"], dataset_id=dataset_id)

    # add sample to tag
    test_resolvers["tag"].add_tag_to_sample(tag.tag_id, sample)
    assert len(sample.tags) == 1
    assert sample.tags.index(tag) == 0

    # remove sample to tag
    test_resolvers["tag"].remove_tag_from_sample(tag.tag_id, sample)
    assert len(sample.tags) == 0
    with pytest.raises(ValueError, match="is not in list"):
        sample.tags.index(tag)


def test_add_and_remove_sample_ids_to_tag_id(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_1 = create_tag(
        test_resolvers["tag"], dataset_id=dataset_id, tag_name="tag_all"
    )
    tag_2 = create_tag(
        test_resolvers["tag"], dataset_id=dataset_id, tag_name="tag_odd"
    )

    total_samples = 10
    samples = []
    for i in range(total_samples):
        sample = create_sample(
            test_resolvers["sample"],
            dataset_id=dataset_id,
            file_path_abs=f"sample{i}.png",
        )
        samples.append(sample)

    # add samples to tag_1
    test_resolvers["tag"].add_sample_ids_to_tag_id(
        tag_id=tag_1.tag_id, sample_ids=[sample.sample_id for sample in samples]
    )

    # add every odd samples to tag_2
    test_resolvers["tag"].add_sample_ids_to_tag_id(
        tag_id=tag_2.tag_id,
        sample_ids=[
            sample.sample_id for i, sample in enumerate(samples) if i % 2 == 1
        ],
    )

    # ensure all samples were added to the correct tags
    for i, sample in enumerate(samples):
        assert tag_1 in sample.tags
        if i % 2 == 1:
            assert tag_2 in sample.tags

    # ensure the correct number of samples were added to each tag
    assert len(tag_1.samples) == total_samples
    assert len(tag_2.samples) == total_samples / 2

    # lets remove every even samples from tag_1
    # this results in tag_1 and tag_2 having the same samples
    test_resolvers["tag"].remove_sample_ids_from_tag_id(
        tag_id=tag_1.tag_id,
        sample_ids=[
            sample.sample_id
            for i, sample in enumerate(tag_1.samples)
            if i % 2 == 0
        ],
    )

    assert len(tag_1.samples) == total_samples / 2
    assert len(tag_2.samples) == total_samples / 2
    assert tag_1.samples == tag_2.samples


def test_get_all_by_dataset_id__with_tag_filtering(test_resolvers):
    dataset = create_dataset(test_resolvers["dataset"])
    dataset_id = dataset.dataset_id
    tag_part1 = create_tag(
        test_resolvers["tag"], dataset_id=dataset_id, tag_name="tag_1"
    )
    tag_part2 = create_tag(
        test_resolvers["tag"], dataset_id=dataset_id, tag_name="tag_2"
    )

    total_samples = 10
    samples = []
    for i in range(total_samples):
        sample = create_sample(
            test_resolvers["sample"],
            dataset_id=dataset_id,
            file_path_abs=f"sample{i}.png",
        )
        samples.append(sample)

    # add first half to tag_1
    test_resolvers["tag"].add_sample_ids_to_tag_id(
        tag_id=tag_part1.tag_id,
        sample_ids=[
            sample.sample_id
            for i, sample in enumerate(samples)
            if i < total_samples / 2
        ],
    )

    # add second half to tag_1
    test_resolvers["tag"].add_sample_ids_to_tag_id(
        tag_id=tag_part2.tag_id,
        sample_ids=[
            sample.sample_id
            for i, sample in enumerate(samples)
            if i >= total_samples / 2
        ],
    )

    # Test filtering by tags
    samples_part1 = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id=dataset_id, tag_ids=[tag_part1.tag_id]
    )
    assert len(samples_part1) == int(total_samples / 2)
    assert samples_part1[0].file_path_abs == "sample0.png"

    samples_part2 = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id=dataset_id, tag_ids=[tag_part2.tag_id]
    )
    assert len(samples_part2) == int(total_samples / 2)
    assert samples_part2[0].file_path_abs == "sample5.png"

    # test filtering by both tags
    samples_all = test_resolvers["sample"].get_all_by_dataset_id(
        dataset_id=dataset_id,
        tag_ids=[
            tag_part1.tag_id,
            tag_part2.tag_id,
        ],
    )
    assert len(samples_all) == int(total_samples)
