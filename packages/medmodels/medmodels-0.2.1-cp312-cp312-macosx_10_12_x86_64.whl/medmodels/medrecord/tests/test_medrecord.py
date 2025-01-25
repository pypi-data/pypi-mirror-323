import tempfile
import unittest
from typing import List, Tuple

import pandas as pd
import polars as pl
import pytest

import medmodels.medrecord as mr
from medmodels import MedRecord
from medmodels.medrecord.medrecord import EdgesDirected
from medmodels.medrecord.querying import EdgeOperand, NodeOperand
from medmodels.medrecord.types import Attributes, NodeIndex


def create_nodes() -> List[Tuple[NodeIndex, Attributes]]:
    return [
        ("0", {"lorem": "ipsum", "dolor": "sit"}),
        ("1", {"amet": "consectetur"}),
        ("2", {"adipiscing": "elit"}),
        ("3", {}),
    ]


def create_edges() -> List[Tuple[NodeIndex, NodeIndex, Attributes]]:
    return [
        ("0", "1", {"sed": "do", "eiusmod": "tempor"}),
        ("1", "0", {"sed": "do", "eiusmod": "tempor"}),
        ("1", "2", {"incididunt": "ut"}),
        ("0", "3", {}),
    ]


def create_pandas_nodes_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "index": ["0", "1"],
            "attribute": [1, 2],
        }
    )


def create_second_pandas_nodes_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "index": ["2", "3"],
            "attribute": [2, 3],
        }
    )


def create_pandas_edges_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "source": ["0", "1"],
            "target": ["1", "0"],
            "attribute": [1, 2],
        }
    )


def create_second_pandas_edges_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "source": ["0", "1"],
            "target": ["1", "0"],
            "attribute": [2, 3],
        }
    )


def create_medrecord() -> MedRecord:
    return MedRecord.from_tuples(create_nodes(), create_edges())


class TestMedRecord(unittest.TestCase):
    def test_from_tuples(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.node_count() == 4
        assert medrecord.edge_count() == 4

    def test_invalid_from_tuples(self) -> None:
        nodes = create_nodes()

        # Adding an edge pointing to a non-existent node should fail
        with pytest.raises(IndexError):
            MedRecord.from_tuples(nodes, [("0", "50", {})])

        # Adding an edge from a non-existing node should fail
        with pytest.raises(IndexError):
            MedRecord.from_tuples(nodes, [("50", "0", {})])

    def test_from_pandas(self) -> None:
        medrecord = MedRecord.from_pandas(
            (create_pandas_nodes_dataframe(), "index"),
        )

        assert medrecord.node_count() == 2
        assert medrecord.edge_count() == 0

        medrecord = MedRecord.from_pandas(
            [
                (create_pandas_nodes_dataframe(), "index"),
                (create_second_pandas_nodes_dataframe(), "index"),
            ],
        )

        assert medrecord.node_count() == 4
        assert medrecord.edge_count() == 0

        medrecord = MedRecord.from_pandas(
            (create_pandas_nodes_dataframe(), "index"),
            (create_pandas_edges_dataframe(), "source", "target"),
        )

        assert medrecord.node_count() == 2
        assert medrecord.edge_count() == 2

        medrecord = MedRecord.from_pandas(
            [
                (create_pandas_nodes_dataframe(), "index"),
                (create_second_pandas_nodes_dataframe(), "index"),
            ],
            (create_pandas_edges_dataframe(), "source", "target"),
        )

        assert medrecord.node_count() == 4
        assert medrecord.edge_count() == 2

        medrecord = MedRecord.from_pandas(
            (create_pandas_nodes_dataframe(), "index"),
            [
                (create_pandas_edges_dataframe(), "source", "target"),
                (create_second_pandas_edges_dataframe(), "source", "target"),
            ],
        )

        assert medrecord.node_count() == 2
        assert medrecord.edge_count() == 4

        medrecord = MedRecord.from_pandas(
            [
                (create_pandas_nodes_dataframe(), "index"),
                (create_second_pandas_nodes_dataframe(), "index"),
            ],
            [
                (create_pandas_edges_dataframe(), "source", "target"),
                (create_second_pandas_edges_dataframe(), "source", "target"),
            ],
        )

        assert medrecord.node_count() == 4
        assert medrecord.edge_count() == 4

    def test_from_polars(self) -> None:
        nodes = pl.from_pandas(create_pandas_nodes_dataframe())
        second_nodes = pl.from_pandas(create_second_pandas_nodes_dataframe())
        edges = pl.from_pandas(create_pandas_edges_dataframe())
        second_edges = pl.from_pandas(create_second_pandas_edges_dataframe())

        medrecord = MedRecord.from_polars((nodes, "index"), (edges, "source", "target"))

        assert medrecord.node_count() == 2
        assert medrecord.edge_count() == 2

        medrecord = MedRecord.from_polars(
            [(nodes, "index"), (second_nodes, "index")], (edges, "source", "target")
        )

        assert medrecord.node_count() == 4
        assert medrecord.edge_count() == 2

        medrecord = MedRecord.from_polars(
            (nodes, "index"),
            [(edges, "source", "target"), (second_edges, "source", "target")],
        )

        assert medrecord.node_count() == 2
        assert medrecord.edge_count() == 4

        medrecord = MedRecord.from_polars(
            [(nodes, "index"), (second_nodes, "index")],
            [(edges, "source", "target"), (second_edges, "source", "target")],
        )

        assert medrecord.node_count() == 4
        assert medrecord.edge_count() == 4

    def test_invalid_from_polars(self) -> None:
        nodes = pl.from_pandas(create_pandas_nodes_dataframe())
        second_nodes = pl.from_pandas(create_second_pandas_nodes_dataframe())
        edges = pl.from_pandas(create_pandas_edges_dataframe())
        second_edges = pl.from_pandas(create_second_pandas_edges_dataframe())

        # Providing the wrong node index column name should fail
        with pytest.raises(RuntimeError):
            MedRecord.from_polars((nodes, "invalid"), (edges, "source", "target"))

        # Providing the wrong node index column name should fail
        with pytest.raises(RuntimeError):
            MedRecord.from_polars(
                [(nodes, "index"), (second_nodes, "invalid")],
                (edges, "source", "target"),
            )

        # Providing the wrong source index column name should fail
        with pytest.raises(RuntimeError):
            MedRecord.from_polars((nodes, "index"), (edges, "invalid", "target"))

        # Providing the wrong source index column name should fail
        with pytest.raises(RuntimeError):
            MedRecord.from_polars(
                (nodes, "index"),
                [(edges, "source", "target"), (second_edges, "invalid", "target")],
            )

        # Providing the wrong target index column name should fail
        with pytest.raises(RuntimeError):
            MedRecord.from_polars((nodes, "index"), (edges, "source", "invalid"))

        # Providing the wrong target index column name should fail
        with pytest.raises(RuntimeError):
            MedRecord.from_polars(
                (nodes, "index"),
                [(edges, "source", "target"), (edges, "source", "invalid")],
            )

    def test_from_simple_example_dataset(self) -> None:
        medrecord = MedRecord.from_simple_example_dataset()

        assert medrecord.node_count() == 73
        assert medrecord.edge_count() == 160

        assert len(medrecord.nodes_in_group("patient")) == 5
        assert len(medrecord.nodes_in_group("diagnosis")) == 25
        assert len(medrecord.nodes_in_group("drug")) == 19
        assert len(medrecord.nodes_in_group("procedure")) == 24

        assert len(medrecord.edges_in_group("patient_diagnosis")) == 60
        assert len(medrecord.edges_in_group("patient_drug")) == 50
        assert len(medrecord.edges_in_group("patient_procedure")) == 50

    def test_from_advanced_example_dataset(self) -> None:
        medrecord = MedRecord.from_advanced_example_dataset()

        assert medrecord.node_count() == 1088
        assert medrecord.edge_count() == 16883

        assert len(medrecord.nodes_in_group("patient")) == 600
        assert len(medrecord.nodes_in_group("diagnosis")) == 206
        assert len(medrecord.nodes_in_group("drug")) == 185
        assert len(medrecord.nodes_in_group("procedure")) == 96

        assert len(medrecord.edges_in_group("patient_diagnosis")) == 5741
        assert len(medrecord.edges_in_group("patient_drug")) == 10373
        assert len(medrecord.edges_in_group("patient_procedure")) == 677
        assert len(medrecord.edges_in_group("patient_event")) == 92

    def test_ron(self) -> None:
        medrecord = create_medrecord()

        with tempfile.NamedTemporaryFile() as f:
            medrecord.to_ron(f.name)

            loaded_medrecord = MedRecord.from_ron(f.name)

        assert medrecord.node_count() == loaded_medrecord.node_count()
        assert medrecord.edge_count() == loaded_medrecord.edge_count()

    def test_schema(self) -> None:
        schema = mr.Schema(
            groups={
                "group": mr.GroupSchema(
                    nodes={"attribute2": mr.Int()}, edges={"attribute2": mr.Int()}
                )
            },
            default=mr.GroupSchema(
                nodes={"attribute": mr.Int()}, edges={"attribute": mr.Int()}
            ),
        )

        medrecord = MedRecord.with_schema(schema)
        medrecord.add_group("group")

        medrecord.add_nodes(("0", {"attribute": 1}))

        with pytest.raises(
            ValueError,
            match=r"Attribute [^\s]+ of node with index [^\s]+ is of type [^\s]+. Expected [^\s]+.",
        ):
            medrecord.add_nodes(("1", {"attribute": "1"}))

        medrecord.add_nodes(("1", {"attribute": 1, "attribute2": 1}))

        medrecord.add_nodes_to_group("group", "1")

        medrecord.add_nodes(("2", {"attribute": 1, "attribute2": "1"}))

        with pytest.raises(
            ValueError,
            match=r"Attribute [^\s]+ of node with index [^\s]+ is of type [^\s]+. Expected [^\s]+.",
        ):
            medrecord.add_nodes_to_group("group", "2")

        medrecord.add_edges(("0", "1", {"attribute": 1}))

        with pytest.raises(
            ValueError,
            match=r"Attribute [^\s]+ of edge with index [^\s]+ is of type [^\s]+. Expected [^\s]+.",
        ):
            medrecord.add_edges(("0", "1", {"attribute": "1"}))

        edge_index = medrecord.add_edges(("0", "1", {"attribute": 1, "attribute2": 1}))

        medrecord.add_edges_to_group("group", edge_index)

        edge_index = medrecord.add_edges(
            (
                "0",
                "1",
                {"attribute": 1, "attribute2": "1"},
            )
        )

        with pytest.raises(
            ValueError,
            match=r"Attribute [^\s]+ of edge with index [^\s]+ is of type [^\s]+. Expected [^\s]+.",
        ):
            medrecord.add_edges_to_group("group", edge_index)

    def test_nodes(self) -> None:
        medrecord = create_medrecord()

        nodes = [x[0] for x in create_nodes()]

        for node in medrecord.nodes:
            assert node in nodes

    def test_edges(self) -> None:
        medrecord = create_medrecord()

        edges = list(range(len(create_edges())))

        for edge in medrecord.edges:
            assert edge in edges

    def test_groups(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0")

        assert medrecord.groups == ["0"]

    def test_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0")

        assert medrecord.group("0") == {"nodes": [], "edges": []}

        medrecord.add_group("1", ["0"], [0])

        assert medrecord.group("1") == {"nodes": ["0"], "edges": [0]}

        assert medrecord.group(["0", "1"]) == {
            "0": {"nodes": [], "edges": []},
            "1": {"nodes": ["0"], "edges": [0]},
        }

    def test_invalid_group(self) -> None:
        medrecord = create_medrecord()

        # Querying a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.group("0")

        medrecord.add_group("1", ["0"])

        # Querying a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.group(["0", "50"])

    def test_outgoing_edges(self) -> None:
        medrecord = create_medrecord()

        edges = medrecord.outgoing_edges("0")

        assert sorted([0, 3]) == sorted(edges)

        edges = medrecord.outgoing_edges(["0", "1"])

        assert {key: sorted(value) for key, value in edges.items()} == {
            "0": sorted([0, 3]),
            "1": [1, 2],
        }

        def query(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        edges = medrecord.outgoing_edges(query)

        assert {key: sorted(value) for key, value in edges.items()} == {
            "0": sorted([0, 3]),
            "1": [1, 2],
        }

    def test_invalid_outgoing_edges(self) -> None:
        medrecord = create_medrecord()

        # Querying outgoing edges of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.outgoing_edges("50")

        # Querying outgoing edges of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.outgoing_edges(["0", "50"])

    def test_incoming_edges(self) -> None:
        medrecord = create_medrecord()

        edges = medrecord.incoming_edges("1")

        assert edges == [0]

        edges = medrecord.incoming_edges(["1", "2"])

        assert edges == {"1": [0], "2": [2]}

        def query(node: NodeOperand) -> None:
            node.index().is_in(["1", "2"])

        edges = medrecord.incoming_edges(query)

        assert edges == {"1": [0], "2": [2]}

    def test_invalid_incoming_edges(self) -> None:
        medrecord = create_medrecord()

        # Querying incoming edges of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.incoming_edges("50")

        # Querying incoming edges of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.incoming_edges(["0", "50"])

    def test_edge_endpoints(self) -> None:
        medrecord = create_medrecord()

        endpoints = medrecord.edge_endpoints(0)

        assert endpoints == ("0", "1")

        endpoints = medrecord.edge_endpoints([0, 1])

        assert endpoints == {0: ("0", "1"), 1: ("1", "0")}

        def query(edge: EdgeOperand) -> None:
            edge.index().is_in([0, 1])

        endpoints = medrecord.edge_endpoints(query)

        assert endpoints == {0: ("0", "1"), 1: ("1", "0")}

    def test_invalid_edge_endpoints(self) -> None:
        medrecord = create_medrecord()

        # Querying endpoints of a non-existing edge should fail
        with pytest.raises(IndexError):
            medrecord.edge_endpoints(50)

        # Querying endpoints of a non-existing edge should fail
        with pytest.raises(IndexError):
            medrecord.edge_endpoints([0, 50])

    def test_edges_connecting(self) -> None:
        medrecord = create_medrecord()

        edges = medrecord.edges_connecting("0", "1")

        assert edges == [0]

        edges = medrecord.edges_connecting(["0", "1"], "1")

        assert edges == [0]

        def query1(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        edges = medrecord.edges_connecting(query1, "1")

        assert edges == [0]

        edges = medrecord.edges_connecting("0", ["1", "3"])

        assert sorted([0, 3]) == sorted(edges)

        def query2(node: NodeOperand) -> None:
            node.index().is_in(["1", "3"])

        edges = medrecord.edges_connecting("0", query2)

        assert sorted([0, 3]) == sorted(edges)

        edges = medrecord.edges_connecting(["0", "1"], ["1", "2", "3"])

        assert sorted([0, 2, 3]) == sorted(edges)

        def query3(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        def query4(node: NodeOperand) -> None:
            node.index().is_in(["1", "2", "3"])

        edges = medrecord.edges_connecting(query3, query4)

        assert sorted([0, 2, 3]) == sorted(edges)

        edges = medrecord.edges_connecting("0", "1", directed=EdgesDirected.UNDIRECTED)

        assert sorted(edges) == [0, 1]

    def test_remove_nodes(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.node_count() == 4

        attributes = medrecord.remove_nodes("0")

        assert medrecord.node_count() == 3
        assert create_nodes()[0][1] == attributes

        attributes = medrecord.remove_nodes(["1", "2"])

        assert medrecord.node_count() == 1
        assert attributes == {"1": create_nodes()[1][1], "2": create_nodes()[2][1]}

        medrecord = create_medrecord()

        assert medrecord.node_count() == 4

        def query(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        attributes = medrecord.remove_nodes(query)

        assert medrecord.node_count() == 2
        assert attributes == {"0": create_nodes()[0][1], "1": create_nodes()[1][1]}

    def test_invalid_remove_nodes(self) -> None:
        medrecord = create_medrecord()

        # Removing a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.remove_nodes("50")

        # Removing a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.remove_nodes(["0", "50"])

    def test_add_nodes(self) -> None:
        medrecord = MedRecord()

        assert medrecord.node_count() == 0

        medrecord.add_nodes(create_nodes())

        assert medrecord.node_count() == 4

        # Adding node tuple
        medrecord = MedRecord()

        assert medrecord.node_count() == 0

        medrecord.add_nodes(("0", {}))

        assert medrecord.node_count() == 1
        assert len(medrecord.groups) == 0

        medrecord = MedRecord()

        medrecord.add_nodes(("0", {}), "0")

        assert "0" in medrecord.nodes_in_group("0")
        assert len(medrecord.groups) == 1

        # Adding tuple to a group
        medrecord = MedRecord()

        medrecord.add_nodes(create_nodes(), "0")

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")
        assert "2" in medrecord.nodes_in_group("0")
        assert "3" in medrecord.nodes_in_group("0")
        assert "0" in medrecord.groups

        # Adding group without nodes
        medrecord = MedRecord()

        medrecord.add_nodes([], "0")

        assert medrecord.node_count() == 0
        assert "0" in medrecord.groups

        # Adding pandas dataframe
        medrecord = MedRecord()

        assert medrecord.node_count() == 0

        medrecord.add_nodes((create_pandas_nodes_dataframe(), "index"))

        assert medrecord.node_count() == 2

        # Adding pandas dataframe to a group
        medrecord = MedRecord()

        medrecord.add_nodes((create_pandas_nodes_dataframe(), "index"), "0")

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")

        # Adding polars dataframe
        medrecord = MedRecord()

        assert medrecord.node_count() == 0

        nodes = pl.from_pandas(create_pandas_nodes_dataframe())

        medrecord.add_nodes((nodes, "index"))

        assert medrecord.node_count() == 2

        # Adding polars dataframe to a group
        medrecord = MedRecord()

        medrecord.add_nodes((nodes, "index"), "0")

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")

        # Adding multiple pandas dataframes
        medrecord = MedRecord()

        assert medrecord.node_count() == 0

        medrecord.add_nodes(
            [
                (create_pandas_nodes_dataframe(), "index"),
                (create_second_pandas_nodes_dataframe(), "index"),
            ]
        )

        assert medrecord.node_count() == 4

        # Adding multiple pandas dataframes to a group
        medrecord = MedRecord()

        medrecord.add_nodes(
            [
                (create_pandas_nodes_dataframe(), "index"),
                (create_second_pandas_nodes_dataframe(), "index"),
            ],
            group="0",
        )

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")
        assert "2" in medrecord.nodes_in_group("0")
        assert "3" in medrecord.nodes_in_group("0")

        # Checking if nodes can be added to a group that already exists
        medrecord = MedRecord()

        medrecord.add_nodes((create_pandas_nodes_dataframe(), "index"), group="0")

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")
        assert "2" not in medrecord.nodes_in_group("0")
        assert "3" not in medrecord.nodes_in_group("0")

        medrecord.add_nodes(
            (create_second_pandas_nodes_dataframe(), "index"), group="0"
        )

        assert "2" in medrecord.nodes_in_group("0")
        assert "3" in medrecord.nodes_in_group("0")

        # Adding multiple polars dataframes
        medrecord = MedRecord()

        second_nodes = pl.from_pandas(create_second_pandas_nodes_dataframe())

        assert medrecord.node_count() == 0

        medrecord.add_nodes(
            [
                (nodes, "index"),
                (second_nodes, "index"),
            ]
        )

        assert medrecord.node_count() == 4

        # Adding multiple polars dataframes to a group
        medrecord = MedRecord()

        medrecord.add_nodes(
            [
                (nodes, "index"),
                (second_nodes, "index"),
            ],
            group="0",
        )

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")
        assert "2" in medrecord.nodes_in_group("0")
        assert "3" in medrecord.nodes_in_group("0")

    def test_invalid_add_nodes(self) -> None:
        medrecord = create_medrecord()

        with pytest.raises(AssertionError):
            medrecord.add_nodes(create_nodes())

    def test_add_nodes_pandas(self) -> None:
        medrecord = MedRecord()

        nodes = (create_pandas_nodes_dataframe(), "index")

        assert medrecord.node_count() == 0

        medrecord.add_nodes_pandas(nodes)

        assert medrecord.node_count() == 2

        medrecord = MedRecord()

        second_nodes = (create_second_pandas_nodes_dataframe(), "index")

        assert medrecord.node_count() == 0

        medrecord.add_nodes_pandas([nodes, second_nodes])

        assert medrecord.node_count() == 4

        # Trying with the group argument
        medrecord = MedRecord()

        medrecord.add_nodes_pandas(nodes, group="0")

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")

        medrecord = MedRecord()

        medrecord.add_nodes_pandas([], group="0")

        assert medrecord.node_count() == 0
        assert "0" in medrecord.groups

        medrecord = MedRecord()

        medrecord.add_nodes_pandas([nodes, second_nodes], group="0")

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")
        assert "2" in medrecord.nodes_in_group("0")
        assert "3" in medrecord.nodes_in_group("0")

    def test_add_nodes_polars(self) -> None:
        medrecord = MedRecord()

        nodes = pl.from_pandas(create_pandas_nodes_dataframe())

        assert medrecord.node_count() == 0

        medrecord.add_nodes_polars((nodes, "index"))

        assert medrecord.node_count() == 2

        medrecord = MedRecord()

        second_nodes = pl.from_pandas(create_second_pandas_nodes_dataframe())

        assert medrecord.node_count() == 0

        medrecord.add_nodes_polars([(nodes, "index"), (second_nodes, "index")])

        assert medrecord.node_count() == 4

        # Trying with the group argument
        medrecord = MedRecord()

        medrecord.add_nodes_polars((nodes, "index"), group="0")

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")

        medrecord = MedRecord()

        medrecord.add_nodes_polars([], group="0")

        assert medrecord.node_count() == 0
        assert "0" in medrecord.groups

        medrecord = MedRecord()

        medrecord.add_nodes_polars(
            [(nodes, "index"), (second_nodes, "index")], group="0"
        )

        assert "0" in medrecord.nodes_in_group("0")
        assert "1" in medrecord.nodes_in_group("0")
        assert "2" in medrecord.nodes_in_group("0")
        assert "3" in medrecord.nodes_in_group("0")

    def test_invalid_add_nodes_polars(self) -> None:
        medrecord = MedRecord()

        nodes = pl.from_pandas(create_pandas_nodes_dataframe())
        second_nodes = pl.from_pandas(create_second_pandas_nodes_dataframe())

        # Adding a nodes dataframe with the wrong index column name should fail
        with pytest.raises(RuntimeError):
            medrecord.add_nodes_polars((nodes, "invalid"))

        # Adding a nodes dataframe with the wrong index column name should fail
        with pytest.raises(RuntimeError):
            medrecord.add_nodes_polars([(nodes, "index"), (second_nodes, "invalid")])

    def test_remove_edges(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.edge_count() == 4

        attributes = medrecord.remove_edges(0)

        assert medrecord.edge_count() == 3
        assert create_edges()[0][2] == attributes

        attributes = medrecord.remove_edges([1, 2])

        assert medrecord.edge_count() == 1
        assert attributes == {1: create_edges()[1][2], 2: create_edges()[2][2]}

        medrecord = create_medrecord()

        assert medrecord.edge_count() == 4

        def query(edge: EdgeOperand) -> None:
            edge.index().is_in([0, 1])

        attributes = medrecord.remove_edges(query)

        assert medrecord.edge_count() == 2
        assert attributes == {0: create_edges()[0][2], 1: create_edges()[1][2]}

    def test_invalid_remove_edges(self) -> None:
        medrecord = create_medrecord()

        # Removing a non-existing edge should fail
        with pytest.raises(IndexError):
            medrecord.remove_edges(50)

    def test_add_edges(self) -> None:
        medrecord = MedRecord()

        nodes = create_nodes()

        medrecord.add_nodes(nodes)

        assert medrecord.edge_count() == 0

        medrecord.add_edges(create_edges())

        assert medrecord.edge_count() == 4

        # Adding single edge tuple
        medrecord = create_medrecord()

        assert medrecord.edge_count() == 4

        medrecord.add_edges(("0", "3", {}))

        assert medrecord.edge_count() == 5

        medrecord.add_edges(("3", "0", {}), group="0")

        assert medrecord.edge_count() == 6
        assert 5 in medrecord.edges_in_group("0")

        # Adding tuple to a group
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        medrecord.add_edges(create_edges(), "0")

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")
        assert 2 in medrecord.edges_in_group("0")
        assert 3 in medrecord.edges_in_group("0")

        # Adding pandas dataframe
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        assert medrecord.edge_count() == 0

        medrecord.add_edges((create_pandas_edges_dataframe(), "source", "target"))

        assert medrecord.edge_count() == 2

        # Adding pandas dataframe to a group
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        medrecord.add_edges((create_pandas_edges_dataframe(), "source", "target"), "0")

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")

        # Adding polars dataframe
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        assert medrecord.edge_count() == 0

        edges = pl.from_pandas(create_pandas_edges_dataframe())

        medrecord.add_edges((edges, "source", "target"))

        assert medrecord.edge_count() == 2

        # Adding polars dataframe to a group
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        medrecord.add_edges((edges, "source", "target"), "0")

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")

        # Adding multiple pandas dataframe
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        assert medrecord.edge_count() == 0

        medrecord.add_edges(
            [
                (create_pandas_edges_dataframe(), "source", "target"),
                (create_second_pandas_edges_dataframe(), "source", "target"),
            ]
        )

        assert medrecord.edge_count() == 4

        # Adding multiple pandas dataframe to a group
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        medrecord.add_edges(
            [
                (create_pandas_edges_dataframe(), "source", "target"),
                (create_second_pandas_edges_dataframe(), "source", "target"),
            ],
            "0",
        )

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")
        assert 2 in medrecord.edges_in_group("0")
        assert 3 in medrecord.edges_in_group("0")

        # Adding multiple polars dataframe
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        assert medrecord.edge_count() == 0

        second_edges = pl.from_pandas(create_second_pandas_edges_dataframe())

        medrecord.add_edges(
            [
                (edges, "source", "target"),
                (second_edges, "source", "target"),
            ]
        )

        assert medrecord.edge_count() == 4

        # Adding multiple polars dataframe to a group
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        medrecord.add_edges(
            [
                (edges, "source", "target"),
                (second_edges, "source", "target"),
            ],
            "0",
        )

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")
        assert 2 in medrecord.edges_in_group("0")
        assert 3 in medrecord.edges_in_group("0")

    def test_invalid_add_edges(self) -> None:
        medrecord = MedRecord()

        nodes = create_nodes()

        medrecord.add_nodes(nodes)

        # Adding an edge pointing to a non-existent node should fail
        with pytest.raises(IndexError):
            medrecord.add_edges(("0", "50", {}))

        # Adding an edge from a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.add_edges(("50", "0", {}))

    def test_add_edges_pandas(self) -> None:
        medrecord = MedRecord()

        nodes = create_nodes()

        medrecord.add_nodes(nodes)

        edges = (create_pandas_edges_dataframe(), "source", "target")

        assert medrecord.edge_count() == 0

        medrecord.add_edges(edges)

        assert medrecord.edge_count() == 2

        # Adding to a group
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        medrecord.add_edges(edges, "0")

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")

        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        second_edges = (create_second_pandas_edges_dataframe(), "source", "target")

        medrecord.add_edges([edges, second_edges], "0")

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")
        assert 2 in medrecord.edges_in_group("0")
        assert 3 in medrecord.edges_in_group("0")

    def test_add_edges_polars(self) -> None:
        medrecord = MedRecord()

        nodes = create_nodes()

        medrecord.add_nodes(nodes)

        edges = pl.from_pandas(create_pandas_edges_dataframe())

        assert medrecord.edge_count() == 0

        medrecord.add_edges_polars((edges, "source", "target"))

        assert medrecord.edge_count() == 2

        # Adding to a group
        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        medrecord.add_edges_polars((edges, "source", "target"), "0")

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")

        medrecord = MedRecord()

        medrecord.add_nodes(nodes)

        second_edges = pl.from_pandas(create_second_pandas_edges_dataframe())

        medrecord.add_edges_polars(
            [(edges, "source", "target"), (second_edges, "source", "target")], "0"
        )

        assert 0 in medrecord.edges_in_group("0")
        assert 1 in medrecord.edges_in_group("0")
        assert 2 in medrecord.edges_in_group("0")
        assert 3 in medrecord.edges_in_group("0")

    def test_invalid_add_edges_polars(self) -> None:
        medrecord = MedRecord()

        nodes = create_nodes()

        medrecord.add_nodes(nodes)

        edges = pl.from_pandas(create_pandas_edges_dataframe())

        # Providing the wrong source index column name should fail
        with pytest.raises(RuntimeError):
            medrecord.add_edges_polars((edges, "invalid", "target"))

        # Providing the wrong target index column name should fail
        with pytest.raises(RuntimeError):
            medrecord.add_edges_polars((edges, "source", "invalid"))

    def test_add_group(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.group_count() == 0

        medrecord.add_group("0")

        assert medrecord.group_count() == 1

        medrecord.add_group("1", "0", 0)

        assert medrecord.group_count() == 2
        assert medrecord.group("1") == {"nodes": ["0"], "edges": [0]}

        medrecord.add_group("2", ["0", "1"], [0, 1])

        assert medrecord.group_count() == 3
        nodes_and_edges = medrecord.group("2")
        assert sorted(["0", "1"]) == sorted(nodes_and_edges["nodes"])
        assert sorted([0, 1]) == sorted(nodes_and_edges["edges"])

        def query1(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        def query2(edge: EdgeOperand) -> None:
            edge.index().is_in([0, 1])

        medrecord.add_group(
            "3",
            query1,
            query2,
        )

        assert medrecord.group_count() == 4
        nodes_and_edges = medrecord.group("3")
        assert sorted(["0", "1"]) == sorted(nodes_and_edges["nodes"])
        assert sorted([0, 1]) == sorted(nodes_and_edges["edges"])

    def test_invalid_add_group(self) -> None:
        medrecord = create_medrecord()

        # Adding a group with a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.add_group("0", "50")

        # Adding an already existing group should fail
        with pytest.raises(IndexError):
            medrecord.add_group("0", ["0", "50"])

        medrecord.add_group("0", "0")

        # Adding an already existing group should fail
        with pytest.raises(AssertionError):
            medrecord.add_group("0")

        # Adding a node to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_group("0", "0")

        # Adding a node to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_group("0", ["1", "0"])

        def query(node: NodeOperand) -> None:
            node.index().equal_to("0")

        # Adding a node to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_group("0", query)

    def test_remove_groups(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0")

        assert medrecord.group_count() == 1

        medrecord.remove_groups("0")

        assert medrecord.group_count() == 0

    def test_invalid_remove_groups(self) -> None:
        medrecord = create_medrecord()

        # Removing a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.remove_groups("0")

    def test_add_nodes_to_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0")

        assert medrecord.nodes_in_group("0") == []

        medrecord.add_nodes_to_group("0", "0")

        assert medrecord.nodes_in_group("0") == ["0"]

        medrecord.add_nodes_to_group("0", ["1", "2"])

        assert sorted(["0", "1", "2"]) == sorted(medrecord.nodes_in_group("0"))

        def query(node: NodeOperand) -> None:
            node.index().equal_to("3")

        medrecord.add_nodes_to_group("0", query)

        assert sorted(["0", "1", "2", "3"]) == sorted(medrecord.nodes_in_group("0"))

    def test_invalid_add_nodes_to_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", ["0"])

        # Adding to a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.add_nodes_to_group("50", "1")

        # Adding to a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.add_nodes_to_group("50", ["1", "2"])

        # Adding a non-existing node to a group should fail
        with pytest.raises(IndexError):
            medrecord.add_nodes_to_group("0", "50")

        # Adding a non-existing node to a group should fail
        with pytest.raises(IndexError):
            medrecord.add_nodes_to_group("0", ["1", "50"])

        # Adding a node to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_nodes_to_group("0", "0")

        # Adding a node to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_nodes_to_group("0", ["1", "0"])

        def query(node: NodeOperand) -> None:
            node.index().equal_to("0")

        # Adding a node to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_nodes_to_group("0", query)

    def test_add_edges_to_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0")

        assert medrecord.edges_in_group("0") == []

        medrecord.add_edges_to_group("0", 0)

        assert medrecord.edges_in_group("0") == [0]

        medrecord.add_edges_to_group("0", [1, 2])

        assert sorted([0, 1, 2]) == sorted(medrecord.edges_in_group("0"))

        def query(edge: EdgeOperand) -> None:
            edge.index().equal_to(3)

        medrecord.add_edges_to_group("0", query)

        assert sorted([0, 1, 2, 3]) == sorted(medrecord.edges_in_group("0"))

    def test_invalid_add_edges_to_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", edges=[0])

        # Adding to a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.add_edges_to_group("50", 1)

        # Adding to a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.add_edges_to_group("50", [1, 2])

        # Adding a non-existing edge to a group should fail
        with pytest.raises(IndexError):
            medrecord.add_edges_to_group("0", 50)

        # Adding a non-existing edge to a group should fail
        with pytest.raises(IndexError):
            medrecord.add_edges_to_group("0", [1, 50])

        # Adding an edge to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_edges_to_group("0", 0)

        # Adding an edge to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_edges_to_group("0", [1, 0])

        def query(edge: EdgeOperand) -> None:
            edge.index().equal_to(0)

        # Adding an edge to a group that already is in the group should fail
        with pytest.raises(AssertionError):
            medrecord.add_edges_to_group("0", query)

    def test_remove_nodes_from_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", ["0", "1"])

        assert sorted(["0", "1"]) == sorted(medrecord.nodes_in_group("0"))

        medrecord.remove_nodes_from_group("0", "1")

        assert medrecord.nodes_in_group("0") == ["0"]

        medrecord.add_nodes_to_group("0", "1")

        assert sorted(["0", "1"]) == sorted(medrecord.nodes_in_group("0"))

        medrecord.remove_nodes_from_group("0", ["0", "1"])

        assert medrecord.nodes_in_group("0") == []

        medrecord.add_nodes_to_group("0", ["0", "1"])

        assert sorted(["0", "1"]) == sorted(medrecord.nodes_in_group("0"))

        def query(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        medrecord.remove_nodes_from_group("0", query)

        assert medrecord.nodes_in_group("0") == []

    def test_invalid_remove_nodes_from_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", ["0", "1"])

        # Removing a node from a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.remove_nodes_from_group("50", "0")

        # Removing a node from a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.remove_nodes_from_group("50", ["0", "1"])

        def query(node: NodeOperand) -> None:
            node.index().equal_to("0")

        # Removing a node from a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.remove_nodes_from_group("50", query)

        # Removing a non-existing node from a group should fail
        with pytest.raises(IndexError):
            medrecord.remove_nodes_from_group("0", "50")

        # Removing a non-existing node from a group should fail
        with pytest.raises(IndexError):
            medrecord.remove_nodes_from_group("0", ["0", "50"])

    def test_remove_edges_from_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", edges=[0, 1])

        assert sorted([0, 1]) == sorted(medrecord.edges_in_group("0"))

        medrecord.remove_edges_from_group("0", 1)

        assert medrecord.edges_in_group("0") == [0]

        medrecord.add_edges_to_group("0", 1)

        assert sorted([0, 1]) == sorted(medrecord.edges_in_group("0"))

        medrecord.remove_edges_from_group("0", [0, 1])

        assert medrecord.edges_in_group("0") == []

        medrecord.add_edges_to_group("0", [0, 1])

        assert sorted([0, 1]) == sorted(medrecord.edges_in_group("0"))

        def query(edge: EdgeOperand) -> None:
            edge.index().is_in([0, 1])

        medrecord.remove_edges_from_group("0", query)

        assert medrecord.edges_in_group("0") == []

    def test_invalid_remove_edges_from_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", edges=[0, 1])

        # Removing an edge from a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.remove_edges_from_group("50", 0)

        # Removing an edge from a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.remove_edges_from_group("50", [0, 1])

        def query(edge: EdgeOperand) -> None:
            edge.index().equal_to(0)

        # Removing an edge from a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.remove_edges_from_group("50", query)

        # Removing a non-existing edge from a group should fail
        with pytest.raises(IndexError):
            medrecord.remove_edges_from_group("0", 50)

        # Removing a non-existing edge from a group should fail
        with pytest.raises(IndexError):
            medrecord.remove_edges_from_group("0", [0, 50])

    def test_nodes_in_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", ["0", "1"])

        assert sorted(["0", "1"]) == sorted(medrecord.nodes_in_group("0"))

    def test_invalid_nodes_in_group(self) -> None:
        medrecord = create_medrecord()

        # Querying nodes in a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.nodes_in_group("50")

    def test_edges_in_group(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", edges=[0, 1])

        assert sorted([0, 1]) == sorted(medrecord.edges_in_group("0"))

    def test_invalid_edges_in_group(self) -> None:
        medrecord = create_medrecord()

        # Querying edges in a non-existing group should fail
        with pytest.raises(IndexError):
            medrecord.edges_in_group("50")

    def test_groups_of_node(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", ["0", "1"])

        assert medrecord.groups_of_node("0") == ["0"]

        assert medrecord.groups_of_node(["0", "1"]) == {"0": ["0"], "1": ["0"]}

        def query(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        assert medrecord.groups_of_node(query) == {"0": ["0"], "1": ["0"]}

    def test_invalid_groups_of_node(self) -> None:
        medrecord = create_medrecord()

        # Querying groups of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.groups_of_node("50")

        # Querying groups of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.groups_of_node(["0", "50"])

    def test_groups_of_edge(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("0", edges=[0, 1])

        assert medrecord.groups_of_edge(0) == ["0"]

        assert medrecord.groups_of_edge([0, 1]) == {0: ["0"], 1: ["0"]}

        def query(edge: EdgeOperand) -> None:
            edge.index().is_in([0, 1])

        assert medrecord.groups_of_edge(query) == {0: ["0"], 1: ["0"]}

    def test_invalid_groups_of_edge(self) -> None:
        medrecord = create_medrecord()

        # Querying groups of a non-existing edge should fail
        with pytest.raises(IndexError):
            medrecord.groups_of_edge(50)

        # Querying groups of a non-existing edge should fail
        with pytest.raises(IndexError):
            medrecord.groups_of_edge([0, 50])

    def test_node_count(self) -> None:
        medrecord = MedRecord()

        assert medrecord.node_count() == 0

        medrecord.add_nodes([("0", {})])

        assert medrecord.node_count() == 1

    def test_edge_count(self) -> None:
        medrecord = MedRecord()

        medrecord.add_nodes(("0", {}))
        medrecord.add_nodes(("1", {}))

        assert medrecord.edge_count() == 0

        medrecord.add_edges(("0", "1", {}))

        assert medrecord.edge_count() == 1

    def test_group_count(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.group_count() == 0

        medrecord.add_group("0")

        assert medrecord.group_count() == 1

    def test_contains_node(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.contains_node("0")

        assert not medrecord.contains_node("50")

    def test_contains_edge(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.contains_edge(0)

        assert not medrecord.contains_edge(50)

    def test_contains_group(self) -> None:
        medrecord = create_medrecord()

        assert not medrecord.contains_group("0")

        medrecord.add_group("0")

        assert medrecord.contains_group("0")

    def test_neighbors(self) -> None:
        medrecord = create_medrecord()

        neighbors = medrecord.neighbors("0")

        assert sorted(["1", "3"]) == sorted(neighbors)

        neighbors = medrecord.neighbors(["0", "1"])

        assert {key: sorted(value) for key, value in neighbors.items()} == {
            "0": sorted(["1", "3"]),
            "1": ["0", "2"],
        }

        def query1(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        neighbors = medrecord.neighbors(query1)

        assert {key: sorted(value) for key, value in neighbors.items()} == {
            "0": sorted(["1", "3"]),
            "1": ["0", "2"],
        }

        neighbors = medrecord.neighbors("0", directed=EdgesDirected.UNDIRECTED)

        assert sorted(["1", "3"]) == sorted(neighbors)

        neighbors = medrecord.neighbors(["0", "1"], directed=EdgesDirected.UNDIRECTED)

        assert {key: sorted(value) for key, value in neighbors.items()} == {
            "0": sorted(["1", "3"]),
            "1": ["0", "2"],
        }

        def query2(node: NodeOperand) -> None:
            node.index().is_in(["0", "1"])

        neighbors = medrecord.neighbors(query2, directed=EdgesDirected.UNDIRECTED)

        assert {key: sorted(value) for key, value in neighbors.items()} == {
            "0": sorted(["1", "3"]),
            "1": ["0", "2"],
        }

    def test_invalid_neighbors(self) -> None:
        medrecord = create_medrecord()

        # Querying neighbors of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.neighbors("50")

        # Querying neighbors of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.neighbors(["0", "50"])

        # Querying undirected neighbors of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.neighbors("50", directed=EdgesDirected.UNDIRECTED)

        # Querying undirected neighbors of a non-existing node should fail
        with pytest.raises(IndexError):
            medrecord.neighbors(["0", "50"], directed=EdgesDirected.UNDIRECTED)

    def test_clear(self) -> None:
        medrecord = create_medrecord()

        assert medrecord.node_count() == 4
        assert medrecord.edge_count() == 4
        assert medrecord.group_count() == 0

        medrecord.clear()

        assert medrecord.node_count() == 0
        assert medrecord.edge_count() == 0
        assert medrecord.group_count() == 0

    def test_clone(self) -> None:
        medrecord = create_medrecord()

        cloned_medrecord = medrecord.clone()

        assert medrecord.node_count() == cloned_medrecord.node_count()
        assert medrecord.edge_count() == cloned_medrecord.edge_count()
        assert medrecord.group_count() == cloned_medrecord.group_count()

        cloned_medrecord.add_nodes(("new_node", {"attribute": "value"}))
        cloned_medrecord.add_edges(("0", "new_node", {"attribute": "value"}))
        cloned_medrecord.add_group("new_group", ["new_node"])

        assert medrecord.node_count() != cloned_medrecord.node_count()
        assert medrecord.edge_count() != cloned_medrecord.edge_count()
        assert medrecord.group_count() != cloned_medrecord.group_count()

    def test_describe_group_nodes(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("Float")
        medrecord.add_group(1, nodes=["2", "0"])

        assert medrecord._describe_group_nodes() == {
            1: {
                "count": 2,
                "attribute": {
                    "adipiscing": {"type": "Categorical", "values": "Values: elit"},
                    "dolor": {"type": "Categorical", "values": "Values: sit"},
                    "lorem": {"type": "Categorical", "values": "Values: ipsum"},
                },
            },
            "Float": {"count": 0, "attribute": {}},
            "Ungrouped Nodes": {
                "count": 2,
                "attribute": {},
            },
        }

        # test group input list
        medrecord.add_group("Odd", nodes=["1", "3"])

        assert medrecord._describe_group_nodes(groups=["Float", "Odd"]) == {
            "Float": {"count": 0, "attribute": {}},
            "Odd": {
                "count": 2,
                "attribute": {
                    "amet": {"type": "Categorical", "values": "Values: consectetur"}
                },
            },
        }

    def test_describe_group_edges(self) -> None:
        medrecord = create_medrecord()

        medrecord.add_group("Even", edges=[0, 2])

        assert medrecord._describe_group_edges() == {
            "Even": {
                "count": 2,
                "attribute": {
                    "eiusmod": {"type": "Categorical", "values": "Values: tempor"},
                    "incididunt": {"type": "Categorical", "values": "Values: ut"},
                    "sed": {"type": "Categorical", "values": "Values: do"},
                },
            },
            "Ungrouped Edges": {"count": 2, "attribute": {}},
        }

        # test the specified group list
        assert medrecord._describe_group_edges(groups=["Even"]) == {
            "Even": {
                "count": 2,
                "attribute": {
                    "eiusmod": {"type": "Categorical", "values": "Values: tempor"},
                    "incididunt": {"type": "Categorical", "values": "Values: ut"},
                    "sed": {"type": "Categorical", "values": "Values: do"},
                },
            },
        }

    def test_overview_edges(self) -> None:
        medrecord = MedRecord.from_simple_example_dataset()

        assert "\n".join(
            [
                "--------------------------------------------------------------------------",
                "Edges Group       Count Attribute     Type       Data                     ",
                "--------------------------------------------------------------------------",
                "patient_diagnosis 60    duration_days Continuous min: 0.00                ",
                "                                                 max: 3416.00             ",
                "                                                 mean: 405.02             ",
                "                        time          Temporal   min: 1962-10-21 00:00:00 ",
                "                                                 max: 2024-04-12 00:00:00 ",
                "--------------------------------------------------------------------------",
            ]
        ) == str(medrecord.overview_edges("patient_diagnosis"))


if __name__ == "__main__":
    run_test = unittest.TestLoader().loadTestsFromTestCase(TestMedRecord)
    unittest.TextTestRunner(verbosity=2).run(run_test)
