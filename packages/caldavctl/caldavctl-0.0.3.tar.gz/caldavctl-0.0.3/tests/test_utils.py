# SPDX-FileCopyrightText: 2024-present Helder Guerreiro <helder@tretas.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from caldavctl.utils import deep_merge_dict  # Replace 'your_module' with the actual module name


def test_deep_merge_dict_simple():
    source = {'a': 1, 'b': 2}
    destination = {'b': 3, 'c': 4}
    result = deep_merge_dict(source, destination)
    expected = {'a': 1, 'b': 2, 'c': 4}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_nested():
    source = {'a': {'x': 1}, 'b': 2}
    destination = {'a': {'y': 3}, 'c': 4}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 1, 'y': 3}, 'b': 2, 'c': 4}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_overwrite():
    source = {'a': {'x': 5}, 'b': 6}
    destination = {'a': {'x': 1, 'y': 3}, 'c': 4}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 5, 'y': 3}, 'b': 6, 'c': 4}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_empty_source():
    source = {}
    destination = {'a': 1, 'b': 2}
    result = deep_merge_dict(source, destination)
    expected = {'a': 1, 'b': 2}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_empty_destination():
    source = {'a': {'x': 1}, 'b': 2}
    destination = {}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 1}, 'b': 2}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_conflicting_types():
    source = {'a': {'x': 1}}
    destination = {'a': 5}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 1}}
    assert result == expected
    assert destination == expected  # Ensure in-place modification


def test_deep_merge_dict_nested_empty_dict():
    source = {'a': {}}
    destination = {'a': {'x': 1}}
    result = deep_merge_dict(source, destination)
    expected = {'a': {'x': 1}}
    assert result == expected
    assert destination == expected  # Ensure in-place modification
