import unittest

import pytest

from medmodels import MedRecord
from medmodels.medrecord.querying import EdgeOperand, NodeOperand


def create_medrecord() -> MedRecord:
    return MedRecord.from_tuples(
        [
            (0, {"foo": "bar", "bar": "foo", "lorem": "ipsum"}),
            (1, {"foo": "bar", "bar": "foo"}),
            (2, {"foo": "bar", "bar": "foo"}),
            (3, {"foo": "bar", "bar": "test"}),
        ],
        [
            (0, 1, {"foo": "bar", "bar": "foo", "lorem": "ipsum"}),
            (1, 2, {"foo": "bar", "bar": "foo"}),
            (2, 3, {"foo": "bar", "bar": "foo"}),
            (3, 0, {"foo": "bar", "bar": "test"}),
        ],
    )


def node_greater_than_or_equal_two(node: NodeOperand) -> None:
    node.index().greater_than_or_equal_to(2)


def node_greater_than_three(node: NodeOperand) -> None:
    node.index().greater_than(3)


def node_less_than_two(node: NodeOperand) -> None:
    node.index().less_than(2)


def edge_greater_than_or_equal_two(edge: EdgeOperand) -> None:
    edge.index().greater_than_or_equal_to(2)


def edge_greater_than_three(edge: EdgeOperand) -> None:
    edge.index().greater_than(3)


def edge_less_than_two(edge: EdgeOperand) -> None:
    edge.index().less_than(2)


class TestMedRecord(unittest.TestCase):
    def test_node_getitem(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.node[0] == {"foo": "bar", "bar": "foo", "lorem": "ipsum"}

        # Accessing a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.node[50]

        assert medrecord.node[0, "foo"] == "bar"

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.node[0, "test"]

        assert medrecord.node[0, ["foo", "bar"]] == {"foo": "bar", "bar": "foo"}

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.node[0, ["foo", "test"]]

        assert medrecord.node[0, :] == {"foo": "bar", "bar": "foo", "lorem": "ipsum"}

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[0, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[0, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[0, ::1]

        assert medrecord.node[[0, 1]] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
        }

        with pytest.raises(IndexError):
            medrecord.node[[0, 50]]

        assert medrecord.node[[0, 1], "foo"] == {0: "bar", 1: "bar"}

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.node[[0, 1], "test"]

        # Accessing a key that doesn't exist in all nodes should fail
        with pytest.raises(KeyError):
            medrecord.node[[0, 1], "lorem"]

        assert medrecord.node[[0, 1], ["foo", "bar"]] == {
            0: {"foo": "bar", "bar": "foo"},
            1: {"foo": "bar", "bar": "foo"},
        }

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.node[[0, 1], ["foo", "test"]]

        # Accessing a key that doesn't exist in all nodes should fail
        with pytest.raises(KeyError):
            medrecord.node[[0, 1], ["foo", "lorem"]]

        assert medrecord.node[[0, 1], :] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[[0, 1], 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[[0, 1], :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[[0, 1], ::1]

        assert medrecord.node[node_greater_than_or_equal_two] == {
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        # Empty query should not fail
        assert medrecord.node[node_greater_than_three] == {}

        assert medrecord.node[node_greater_than_or_equal_two, "foo"] == {
            2: "bar",
            3: "bar",
        }

        # Accessing a non-existing key should fail
        with pytest.raises(
            KeyError,
        ):
            medrecord.node[node_greater_than_or_equal_two, "test"]

        assert medrecord.node[node_greater_than_or_equal_two, ["foo", "bar"]] == {
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.node[node_greater_than_or_equal_two, ["foo", "test"]]

        # Accessing a key that doesn't exist in all nodes should fail
        with pytest.raises(KeyError):
            medrecord.node[node_less_than_two, ["foo", "lorem"]]

        assert medrecord.node[node_greater_than_or_equal_two, :] == {
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[node_greater_than_or_equal_two, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[node_greater_than_or_equal_two, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[node_greater_than_or_equal_two, ::1]

        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[::1]

        assert medrecord.node[:, "foo"] == {0: "bar", 1: "bar", 2: "bar", 3: "bar"}

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.node[:, "test"]

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[1:, "foo"]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:1, "foo"]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[::1, "foo"]

        assert medrecord.node[:, ["foo", "bar"]] == {
            0: {"foo": "bar", "bar": "foo"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.node[:, ["foo", "test"]]

        # Accessing a key that doesn't exist in all nodes should fail
        with pytest.raises(KeyError):
            medrecord.node[:, ["foo", "lorem"]]

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[1:, ["foo", "bar"]]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:1, ["foo", "bar"]]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[::1, ["foo", "bar"]]

        assert medrecord.node[:, :] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[1:, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:1, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[::1, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:, ::1]

    def test_node_setitem(self) -> None:
        # Updating existing attributes

        medrecord = create_medrecord()
        medrecord.node[0] = {"foo": "bar", "bar": "test"}
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "test"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Updating a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.node[50] = {"foo": "bar", "test": "test"}

        medrecord = create_medrecord()
        medrecord.node[0, "foo"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[0, ["foo", "bar"]] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[0, :] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "test"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[0, 1:] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[0, :1] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[0, ::1] = "test"

        medrecord = create_medrecord()
        medrecord.node[[0, 1], "foo"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "test", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[[0, 1], ["foo", "bar"]] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "ipsum"},
            1: {"foo": "test", "bar": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[[0, 1], :] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "test"},
            1: {"foo": "test", "bar": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[[0, 1], 1:] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[[0, 1], :1] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[[0, 1], ::1] = "test"

        medrecord = create_medrecord()
        medrecord.node[node_greater_than_or_equal_two] = {"foo": "bar", "bar": "test"}
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "test"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Empty query should not fail
        medrecord.node[node_greater_than_three] = {"foo": "bar", "bar": "test"}

        medrecord = create_medrecord()
        medrecord.node[node_greater_than_or_equal_two, "foo"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "test", "bar": "foo"},
            3: {"foo": "test", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[node_greater_than_or_equal_two, ["foo", "bar"]] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "test", "bar": "test"},
            3: {"foo": "test", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[node_greater_than_or_equal_two, :] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "test", "bar": "test"},
            3: {"foo": "test", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[node_greater_than_or_equal_two, 1:] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[node_greater_than_or_equal_two, :1] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[node_greater_than_or_equal_two, ::1] = "test"

        medrecord = create_medrecord()
        medrecord.node[:, "foo"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "test", "bar": "foo"},
            2: {"foo": "test", "bar": "foo"},
            3: {"foo": "test", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[1:, "foo"] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:1, "foo"] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[::1, "foo"] = "test"

        medrecord = create_medrecord()
        medrecord.node[:, ["foo", "bar"]] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "ipsum"},
            1: {"foo": "test", "bar": "test"},
            2: {"foo": "test", "bar": "test"},
            3: {"foo": "test", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[1:, ["foo", "bar"]] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:1, ["foo", "bar"]] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[::1, ["foo", "bar"]] = "test"

        medrecord = create_medrecord()
        medrecord.node[:, :] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "test"},
            1: {"foo": "test", "bar": "test"},
            2: {"foo": "test", "bar": "test"},
            3: {"foo": "test", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[1:, :] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:1, :] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[::1, :] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:, 1:] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:, :1] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.node[:, ::1] = "test"

        # Adding new attributes

        medrecord = create_medrecord()
        medrecord.node[0, "test"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum", "test": "test"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[0, ["test", "test2"]] = "test"
        assert medrecord.node[:] == {
            0: {
                "foo": "bar",
                "bar": "foo",
                "lorem": "ipsum",
                "test": "test",
                "test2": "test",
            },
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[[0, 1], "test"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "test": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[[0, 1], ["test", "test2"]] = "test"
        assert medrecord.node[:] == {
            0: {
                "foo": "bar",
                "bar": "foo",
                "lorem": "ipsum",
                "test": "test",
                "test2": "test",
            },
            1: {"foo": "bar", "bar": "foo", "test": "test", "test2": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[node_greater_than_or_equal_two, "test"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo", "test": "test"},
            3: {"foo": "bar", "bar": "test", "test": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[node_greater_than_or_equal_two, ["test", "test2"]] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo", "test": "test", "test2": "test"},
            3: {"foo": "bar", "bar": "test", "test": "test", "test2": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[:, "test"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "test": "test"},
            2: {"foo": "bar", "bar": "foo", "test": "test"},
            3: {"foo": "bar", "bar": "test", "test": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[:, ["test", "test2"]] = "test"
        assert medrecord.node[:] == {
            0: {
                "foo": "bar",
                "bar": "foo",
                "lorem": "ipsum",
                "test": "test",
                "test2": "test",
            },
            1: {"foo": "bar", "bar": "foo", "test": "test", "test2": "test"},
            2: {"foo": "bar", "bar": "foo", "test": "test", "test2": "test"},
            3: {"foo": "bar", "bar": "test", "test": "test", "test2": "test"},
        }

        # Adding and updating attributes

        medrecord = create_medrecord()
        medrecord.node[[0, 1], "lorem"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[[0, 1], ["lorem", "test"]] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[node_less_than_two, "lorem"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[node_less_than_two, ["lorem", "test"]] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[:, "lorem"] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test"},
            2: {"foo": "bar", "bar": "foo", "lorem": "test"},
            3: {"foo": "bar", "bar": "test", "lorem": "test"},
        }

        medrecord = create_medrecord()
        medrecord.node[:, ["lorem", "test"]] = "test"
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            2: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            3: {"foo": "bar", "bar": "test", "lorem": "test", "test": "test"},
        }

    def test_node_delitem(self) -> None:
        medrecord = create_medrecord()
        del medrecord.node[0, "foo"]
        assert medrecord.node[:] == {
            0: {"bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing from a non-existing node should fail
        with pytest.raises(IndexError):
            del medrecord.node[50, "foo"]

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.node[0, "test"]

        medrecord = create_medrecord()
        del medrecord.node[0, ["foo", "bar"]]
        assert medrecord.node[:] == {
            0: {"lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.node[0, ["foo", "test"]]

        medrecord = create_medrecord()
        del medrecord.node[0, :]
        assert medrecord.node[:] == {
            0: {},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[0, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[0, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[0, ::1]

        medrecord = create_medrecord()
        del medrecord.node[[0, 1], "foo"]
        assert medrecord.node[:] == {
            0: {"bar": "foo", "lorem": "ipsum"},
            1: {"bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing from a non-existing node should fail
        with pytest.raises(IndexError):
            del medrecord.node[[0, 50], "foo"]

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.node[[0, 1], "test"]

        medrecord = create_medrecord()
        del medrecord.node[[0, 1], ["foo", "bar"]]
        assert medrecord.node[:] == {
            0: {"lorem": "ipsum"},
            1: {},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.node[[0, 1], ["foo", "test"]]

        medrecord = create_medrecord()
        # Removing a key that doesn't exist in all nodes should fail
        with pytest.raises(KeyError):
            del medrecord.node[[0, 1], ["foo", "lorem"]]

        medrecord = create_medrecord()
        del medrecord.node[[0, 1], :]
        assert medrecord.node[:] == {
            0: {},
            1: {},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[[0, 1], 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[[0, 1], :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[[0, 1], ::1]

        medrecord = create_medrecord()
        del medrecord.node[node_greater_than_or_equal_two, "foo"]
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"bar": "foo"},
            3: {"bar": "test"},
        }

        medrecord = create_medrecord()
        # Empty query should not fail
        del medrecord.node[node_greater_than_three, "foo"]
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.node[node_greater_than_or_equal_two, "test"]

        medrecord = create_medrecord()
        del medrecord.node[node_greater_than_or_equal_two, ["foo", "bar"]]
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {},
            3: {},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.node[node_greater_than_or_equal_two, ["foo", "test"]]

        medrecord = create_medrecord()
        # Removing a key that doesn't exist in all nodes should fail
        with pytest.raises(KeyError):
            del medrecord.node[node_less_than_two, ["foo", "lorem"]]

        medrecord = create_medrecord()
        del medrecord.node[node_greater_than_or_equal_two, :]
        assert medrecord.node[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {},
            3: {},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[node_greater_than_or_equal_two, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[node_greater_than_or_equal_two, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[node_greater_than_or_equal_two, ::1]

        medrecord = create_medrecord()
        del medrecord.node[:, "foo"]
        assert medrecord.node[:] == {
            0: {"bar": "foo", "lorem": "ipsum"},
            1: {"bar": "foo"},
            2: {"bar": "foo"},
            3: {"bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.node[:, "test"]

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[1:, "foo"]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[:1, "foo"]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[::1, "foo"]

        medrecord = create_medrecord()
        del medrecord.node[:, ["foo", "bar"]]
        assert medrecord.node[:] == {0: {"lorem": "ipsum"}, 1: {}, 2: {}, 3: {}}

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.node[:, ["foo", "test"]]

        medrecord = create_medrecord()
        # Removing a key that doesn't exist in all nodes should fail
        with pytest.raises(KeyError):
            del medrecord.node[:, ["foo", "lorem"]]

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[1:, ["foo", "bar"]]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[:1, ["foo", "bar"]]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[::1, ["foo", "bar"]]

        medrecord = create_medrecord()
        del medrecord.node[:, :]
        assert medrecord.node[:] == {0: {}, 1: {}, 2: {}, 3: {}}

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[1:, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[:1, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[::1, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[:, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[:, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.node[:, ::1]

    def test_edge_getitem(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.edge[0] == {"foo": "bar", "bar": "foo", "lorem": "ipsum"}

        # Accessing a non-existing edge should fail
        with pytest.raises(IndexError):
            medrecord.edge[50]

        assert medrecord.edge[0, "foo"] == "bar"

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.edge[0, "test"]

        assert medrecord.edge[0, ["foo", "bar"]] == {"foo": "bar", "bar": "foo"}

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.edge[0, ["foo", "test"]]

        assert medrecord.edge[0, :] == {"foo": "bar", "bar": "foo", "lorem": "ipsum"}

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[0, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[0, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[0, ::1]

        assert medrecord.edge[[0, 1]] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
        }

        with pytest.raises(IndexError):
            medrecord.edge[[0, 50]]

        assert medrecord.edge[[0, 1], "foo"] == {0: "bar", 1: "bar"}

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.edge[[0, 1], "test"]

        # Accessing a key that doesn't exist in all edges should fail
        with pytest.raises(KeyError):
            medrecord.edge[[0, 1], "lorem"]

        assert medrecord.edge[[0, 1], ["foo", "bar"]] == {
            0: {"foo": "bar", "bar": "foo"},
            1: {"foo": "bar", "bar": "foo"},
        }

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.edge[[0, 1], ["foo", "test"]]

        # Accessing a key that doesn't exist in all edges should fail
        with pytest.raises(KeyError):
            medrecord.edge[[0, 1], ["foo", "lorem"]]

        assert medrecord.edge[[0, 1], :] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[[0, 1], 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[[0, 1], :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[[0, 1], ::1]

        assert medrecord.edge[edge_greater_than_or_equal_two] == {
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        # Empty query should not fail
        assert medrecord.edge[edge_greater_than_three] == {}

        assert medrecord.edge[edge_greater_than_or_equal_two, "foo"] == {
            2: "bar",
            3: "bar",
        }

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.edge[edge_greater_than_or_equal_two, "test"]

        assert medrecord.edge[edge_greater_than_or_equal_two, ["foo", "bar"]] == {
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.edge[edge_greater_than_or_equal_two, ["foo", "test"]]

        # Accessing a key that doesn't exist in all edges should fail
        with pytest.raises(KeyError):
            medrecord.edge[edge_less_than_two, ["foo", "lorem"]]

        assert medrecord.edge[edge_greater_than_or_equal_two, :] == {
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[edge_greater_than_or_equal_two, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[edge_greater_than_or_equal_two, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[edge_greater_than_or_equal_two, ::1]

        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[::1]

        assert medrecord.edge[:, "foo"] == {0: "bar", 1: "bar", 2: "bar", 3: "bar"}

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.edge[:, "test"]

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[1:, "foo"]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:1, "foo"]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[::1, "foo"]

        assert medrecord.edge[:, ["foo", "bar"]] == {
            0: {"foo": "bar", "bar": "foo"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        # Accessing a non-existing key should fail
        with pytest.raises(KeyError):
            medrecord.edge[:, ["foo", "test"]]

        # Accessing a key that doesn't exist in all edges should fail
        with pytest.raises(KeyError):
            medrecord.edge[:, ["foo", "lorem"]]

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[1:, ["foo", "bar"]]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:1, ["foo", "bar"]]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[::1, ["foo", "bar"]]

        assert medrecord.edge[:, :] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[1:, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:1, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[::1, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:, ::1]

    def test_edge_setitem(self) -> None:
        # Updating existing attributes

        medrecord = create_medrecord()
        medrecord.edge[0] = {"foo": "bar", "bar": "test"}
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "test"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Updating a non-existing edge should fail
        with pytest.raises(IndexError):
            medrecord.edge[50] = {"foo": "bar", "test": "test"}

        medrecord = create_medrecord()
        medrecord.edge[0, "foo"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[0, ["foo", "bar"]] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[0, :] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "test"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[0, 1:] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[0, :1] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[0, ::1] = "test"

        medrecord = create_medrecord()
        medrecord.edge[[0, 1], "foo"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "test", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[[0, 1], ["foo", "bar"]] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "ipsum"},
            1: {"foo": "test", "bar": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[[0, 1], :] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "test"},
            1: {"foo": "test", "bar": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[[0, 1], 1:] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[[0, 1], :1] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[[0, 1], ::1] = "test"

        medrecord = create_medrecord()
        medrecord.edge[edge_greater_than_or_equal_two] = {"foo": "bar", "bar": "test"}
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "test"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Empty query should not fail
        medrecord.edge[edge_greater_than_three] = {"foo": "bar", "bar": "test"}

        medrecord = create_medrecord()
        medrecord.edge[edge_greater_than_or_equal_two, "foo"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "test", "bar": "foo"},
            3: {"foo": "test", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[edge_greater_than_or_equal_two, ["foo", "bar"]] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "test", "bar": "test"},
            3: {"foo": "test", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[edge_greater_than_or_equal_two, :] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "test", "bar": "test"},
            3: {"foo": "test", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[edge_greater_than_or_equal_two, 1:] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[edge_greater_than_or_equal_two, :1] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[edge_greater_than_or_equal_two, ::1] = "test"

        medrecord = create_medrecord()
        medrecord.edge[:, "foo"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "test", "bar": "foo"},
            2: {"foo": "test", "bar": "foo"},
            3: {"foo": "test", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[1:, "foo"] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:1, "foo"] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[::1, "foo"] = "test"

        medrecord = create_medrecord()
        medrecord.edge[:, ["foo", "bar"]] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "ipsum"},
            1: {"foo": "test", "bar": "test"},
            2: {"foo": "test", "bar": "test"},
            3: {"foo": "test", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[1:, ["foo", "bar"]] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:1, ["foo", "bar"]] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[::1, ["foo", "bar"]] = "test"

        medrecord = create_medrecord()
        medrecord.edge[:, :] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "test", "bar": "test", "lorem": "test"},
            1: {"foo": "test", "bar": "test"},
            2: {"foo": "test", "bar": "test"},
            3: {"foo": "test", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[1:, :] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:1, :] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[::1, :] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:, 1:] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:, :1] = "test"
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            medrecord.edge[:, ::1] = "test"

        # Adding new attributes

        medrecord = create_medrecord()
        medrecord.edge[0, "test"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum", "test": "test"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[0, ["test", "test2"]] = "test"
        assert medrecord.edge[:] == {
            0: {
                "foo": "bar",
                "bar": "foo",
                "lorem": "ipsum",
                "test": "test",
                "test2": "test",
            },
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[[0, 1], "test"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "test": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[[0, 1], ["test", "test2"]] = "test"
        assert medrecord.edge[:] == {
            0: {
                "foo": "bar",
                "bar": "foo",
                "lorem": "ipsum",
                "test": "test",
                "test2": "test",
            },
            1: {"foo": "bar", "bar": "foo", "test": "test", "test2": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[edge_greater_than_or_equal_two, "test"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo", "test": "test"},
            3: {"foo": "bar", "bar": "test", "test": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[edge_greater_than_or_equal_two, ["test", "test2"]] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo", "test": "test", "test2": "test"},
            3: {"foo": "bar", "bar": "test", "test": "test", "test2": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[:, "test"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "test": "test"},
            2: {"foo": "bar", "bar": "foo", "test": "test"},
            3: {"foo": "bar", "bar": "test", "test": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[:, ["test", "test2"]] = "test"
        assert medrecord.edge[:] == {
            0: {
                "foo": "bar",
                "bar": "foo",
                "lorem": "ipsum",
                "test": "test",
                "test2": "test",
            },
            1: {"foo": "bar", "bar": "foo", "test": "test", "test2": "test"},
            2: {"foo": "bar", "bar": "foo", "test": "test", "test2": "test"},
            3: {"foo": "bar", "bar": "test", "test": "test", "test2": "test"},
        }

        # Adding and updating attributes

        medrecord = create_medrecord()
        medrecord.edge[[0, 1], "lorem"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[[0, 1], ["lorem", "test"]] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[edge_less_than_two, "lorem"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[edge_less_than_two, ["lorem", "test"]] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[:, "lorem"] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test"},
            2: {"foo": "bar", "bar": "foo", "lorem": "test"},
            3: {"foo": "bar", "bar": "test", "lorem": "test"},
        }

        medrecord = create_medrecord()
        medrecord.edge[:, ["lorem", "test"]] = "test"
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            1: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            2: {"foo": "bar", "bar": "foo", "lorem": "test", "test": "test"},
            3: {"foo": "bar", "bar": "test", "lorem": "test", "test": "test"},
        }

    def test_edge_delitem(self) -> None:
        medrecord = create_medrecord()
        del medrecord.edge[0, "foo"]
        assert medrecord.edge[:] == {
            0: {"bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing from a non-existing edge should fail
        with pytest.raises(IndexError):
            del medrecord.edge[50, "foo"]

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.edge[0, "test"]

        medrecord = create_medrecord()
        del medrecord.edge[0, ["foo", "bar"]]
        assert medrecord.edge[:] == {
            0: {"lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.edge[0, ["foo", "test"]]

        medrecord = create_medrecord()
        del medrecord.edge[0, :]
        assert medrecord.edge[:] == {
            0: {},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[0, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[0, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[0, ::1]

        medrecord = create_medrecord()
        del medrecord.edge[[0, 1], "foo"]
        assert medrecord.edge[:] == {
            0: {"bar": "foo", "lorem": "ipsum"},
            1: {"bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing from a non-existing edge should fail
        with pytest.raises(IndexError):
            del medrecord.edge[[0, 50], "foo"]

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.edge[[0, 1], "test"]

        medrecord = create_medrecord()
        del medrecord.edge[[0, 1], ["foo", "bar"]]
        assert medrecord.edge[:] == {
            0: {"lorem": "ipsum"},
            1: {},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.edge[[0, 1], ["foo", "test"]]

        medrecord = create_medrecord()
        # Removing a key that doesn't exist in all edges should fail
        with pytest.raises(KeyError):
            del medrecord.edge[[0, 1], ["foo", "lorem"]]

        medrecord = create_medrecord()
        del medrecord.edge[[0, 1], :]
        assert medrecord.edge[:] == {
            0: {},
            1: {},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[[0, 1], 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[[0, 1], :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[[0, 1], ::1]

        medrecord = create_medrecord()
        del medrecord.edge[edge_greater_than_or_equal_two, "foo"]
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"bar": "foo"},
            3: {"bar": "test"},
        }

        medrecord = create_medrecord()
        # Empty query should not fail
        del medrecord.edge[edge_greater_than_three, "foo"]
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {"foo": "bar", "bar": "foo"},
            3: {"foo": "bar", "bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.edge[edge_greater_than_or_equal_two, "test"]

        medrecord = create_medrecord()
        del medrecord.edge[edge_greater_than_or_equal_two, ["foo", "bar"]]
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {},
            3: {},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.edge[edge_greater_than_or_equal_two, ["foo", "test"]]

        medrecord = create_medrecord()
        # Removing a key that doesn't exist in all edges should fail
        with pytest.raises(KeyError):
            del medrecord.edge[edge_less_than_two, ["foo", "lorem"]]

        medrecord = create_medrecord()
        del medrecord.edge[edge_greater_than_or_equal_two, :]
        assert medrecord.edge[:] == {
            0: {"foo": "bar", "bar": "foo", "lorem": "ipsum"},
            1: {"foo": "bar", "bar": "foo"},
            2: {},
            3: {},
        }

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[edge_greater_than_or_equal_two, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[edge_greater_than_or_equal_two, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[edge_greater_than_or_equal_two, ::1]

        medrecord = create_medrecord()
        del medrecord.edge[:, "foo"]
        assert medrecord.edge[:] == {
            0: {"bar": "foo", "lorem": "ipsum"},
            1: {"bar": "foo"},
            2: {"bar": "foo"},
            3: {"bar": "test"},
        }

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.edge[:, "test"]

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[1:, "foo"]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[:1, "foo"]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[::1, "foo"]

        medrecord = create_medrecord()
        del medrecord.edge[:, ["foo", "bar"]]
        assert medrecord.edge[:] == {0: {"lorem": "ipsum"}, 1: {}, 2: {}, 3: {}}

        medrecord = create_medrecord()
        # Removing a non-existing key should fail
        with pytest.raises(KeyError):
            del medrecord.edge[:, ["foo", "test"]]

        medrecord = create_medrecord()
        # Removing a key that doesn't exist in all edges should fail
        with pytest.raises(KeyError):
            del medrecord.edge[:, ["foo", "lorem"]]

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[1:, ["foo", "bar"]]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[:1, ["foo", "bar"]]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[::1, ["foo", "bar"]]

        medrecord = create_medrecord()
        del medrecord.edge[:, :]
        assert medrecord.edge[:] == {0: {}, 1: {}, 2: {}, 3: {}}

        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[1:, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[:1, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[::1, :]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[:, 1:]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[:, :1]
        with pytest.raises(ValueError, match="Invalid slice, only ':' is allowed"):
            del medrecord.edge[:, ::1]
