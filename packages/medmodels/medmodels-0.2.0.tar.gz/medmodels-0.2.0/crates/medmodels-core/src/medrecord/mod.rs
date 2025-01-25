mod datatypes;
mod example_dataset;
mod graph;
mod group_mapping;
mod polars;
mod querying;
mod schema;

pub use self::{
    datatypes::{DataType, MedRecordAttribute, MedRecordValue},
    graph::{Attributes, EdgeIndex, NodeIndex},
    group_mapping::Group,
    querying::{
        attributes::{
            AttributesTreeOperand, MultipleAttributesComparisonOperand, MultipleAttributesOperand,
            SingleAttributeComparisonOperand, SingleAttributeOperand,
        },
        edges::{
            EdgeIndexComparisonOperand, EdgeIndexOperand, EdgeIndicesComparisonOperand,
            EdgeIndicesOperand, EdgeOperand,
        },
        nodes::{
            EdgeDirection, NodeIndexComparisonOperand, NodeIndexOperand,
            NodeIndicesComparisonOperand, NodeIndicesOperand, NodeOperand,
        },
        traits::DeepClone,
        values::{
            MultipleValuesComparisonOperand, MultipleValuesOperand, SingleValueComparisonOperand,
            SingleValueOperand,
        },
        wrapper::{CardinalityWrapper, Wrapper},
    },
    schema::{AttributeDataType, AttributeType, GroupSchema, Schema},
};
use crate::errors::MedRecordError;
use ::polars::frame::DataFrame;
use graph::Graph;
use group_mapping::GroupMapping;
use polars::{dataframe_to_edges, dataframe_to_nodes};
use querying::{edges::EdgeSelection, nodes::NodeSelection};
use serde::{Deserialize, Serialize};
use std::{fs, mem, path::Path};

pub struct NodeDataFrameInput {
    dataframe: DataFrame,
    index_column: String,
}

pub struct EdgeDataFrameInput {
    dataframe: DataFrame,
    source_index_column: String,
    target_index_column: String,
}

impl<D, S> From<(D, S)> for NodeDataFrameInput
where
    D: Into<DataFrame>,
    S: Into<String>,
{
    fn from(val: (D, S)) -> Self {
        NodeDataFrameInput {
            dataframe: val.0.into(),
            index_column: val.1.into(),
        }
    }
}

impl<D, S> From<(D, S, S)> for EdgeDataFrameInput
where
    D: Into<DataFrame>,
    S: Into<String>,
{
    fn from(val: (D, S, S)) -> Self {
        EdgeDataFrameInput {
            dataframe: val.0.into(),
            source_index_column: val.1.into(),
            target_index_column: val.2.into(),
        }
    }
}

fn node_dataframes_to_tuples(
    nodes_dataframes: impl IntoIterator<Item = impl Into<NodeDataFrameInput>>,
) -> Result<Vec<(NodeIndex, Attributes)>, MedRecordError> {
    let nodes = nodes_dataframes
        .into_iter()
        .map(|dataframe_input| {
            let dataframe_input = dataframe_input.into();

            dataframe_to_nodes(dataframe_input.dataframe, &dataframe_input.index_column)
        })
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .flatten()
        .collect();

    Ok(nodes)
}

#[allow(clippy::type_complexity)]
fn dataframes_to_tuples(
    nodes_dataframes: impl IntoIterator<Item = impl Into<NodeDataFrameInput>>,
    edges_dataframes: impl IntoIterator<Item = impl Into<EdgeDataFrameInput>>,
) -> Result<
    (
        Vec<(NodeIndex, Attributes)>,
        Vec<(NodeIndex, NodeIndex, Attributes)>,
    ),
    MedRecordError,
> {
    let nodes = node_dataframes_to_tuples(nodes_dataframes)?;

    let edges = edges_dataframes
        .into_iter()
        .map(|dataframe_input| {
            let dataframe_input = dataframe_input.into();

            dataframe_to_edges(
                dataframe_input.dataframe,
                &dataframe_input.source_index_column,
                &dataframe_input.target_index_column,
            )
        })
        .collect::<Result<Vec<_>, _>>()?
        .into_iter()
        .flatten()
        .collect();

    Ok((nodes, edges))
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct MedRecord {
    graph: Graph,
    group_mapping: GroupMapping,
    schema: Schema,
}

impl MedRecord {
    pub fn new() -> Self {
        Self {
            graph: Graph::new(),
            group_mapping: GroupMapping::new(),
            schema: Schema::default(),
        }
    }

    pub fn with_schema(schema: Schema) -> Self {
        Self {
            graph: Graph::new(),
            group_mapping: GroupMapping::new(),
            schema,
        }
    }

    pub fn with_capacity(nodes: usize, edges: usize, schema: Option<Schema>) -> Self {
        Self {
            graph: Graph::with_capacity(nodes, edges),
            group_mapping: GroupMapping::new(),
            schema: schema.unwrap_or_default(),
        }
    }

    pub fn from_tuples(
        nodes: Vec<(NodeIndex, Attributes)>,
        edges: Option<Vec<(NodeIndex, NodeIndex, Attributes)>>,
        schema: Option<Schema>,
    ) -> Result<Self, MedRecordError> {
        let mut medrecord = Self::with_capacity(
            nodes.len(),
            edges.as_ref().map(|vec| vec.len()).unwrap_or(0),
            schema,
        );

        for (node_index, attributes) in nodes {
            medrecord.add_node(node_index, attributes)?;
        }

        if let Some(edges) = edges {
            for (source_node_index, target_node_index, attributes) in edges {
                medrecord.add_edge(source_node_index, target_node_index, attributes)?;
            }
        }

        Ok(medrecord)
    }

    pub fn from_dataframes(
        nodes_dataframes: impl IntoIterator<Item = impl Into<NodeDataFrameInput>>,
        edges_dataframes: impl IntoIterator<Item = impl Into<EdgeDataFrameInput>>,
        schema: Option<Schema>,
    ) -> Result<MedRecord, MedRecordError> {
        let (nodes, edges) = dataframes_to_tuples(nodes_dataframes, edges_dataframes)?;

        Self::from_tuples(nodes, Some(edges), schema)
    }

    pub fn from_nodes_dataframes(
        nodes_dataframes: impl IntoIterator<Item = impl Into<NodeDataFrameInput>>,
        schema: Option<Schema>,
    ) -> Result<MedRecord, MedRecordError> {
        let nodes = node_dataframes_to_tuples(nodes_dataframes)?;

        Self::from_tuples(nodes, None, schema)
    }

    pub fn from_ron<P>(path: P) -> Result<MedRecord, MedRecordError>
    where
        P: AsRef<Path>,
    {
        let file = fs::read_to_string(&path)
            .map_err(|_| MedRecordError::ConversionError("Failed to read file".to_string()))?;

        ron::from_str(&file).map_err(|_| {
            MedRecordError::ConversionError(
                "Failed to create MedRecord from contents from file".to_string(),
            )
        })
    }

    pub fn to_ron<P>(&self, path: P) -> Result<(), MedRecordError>
    where
        P: AsRef<Path>,
    {
        let ron_string = ron::to_string(self).map_err(|_| {
            MedRecordError::ConversionError("Failed to convert MedRecord to ron".to_string())
        })?;

        fs::write(&path, ron_string).map_err(|_| {
            MedRecordError::ConversionError(
                "Failed to save MedRecord due to file error".to_string(),
            )
        })
    }

    pub fn update_schema(&mut self, schema: Schema) -> Result<(), MedRecordError> {
        let mut old_schema = schema;

        mem::swap(&mut self.schema, &mut old_schema);

        let result = self
            .graph
            .nodes
            .iter()
            .map(|(node_index, node)| {
                let groups_of_node = self
                    .groups_of_node(node_index)
                    .expect("groups of node must exist")
                    .collect::<Vec<_>>();

                if !groups_of_node.is_empty() {
                    for group in groups_of_node {
                        self.schema
                            .validate_node(node_index, &node.attributes, Some(group))?;
                    }
                } else {
                    self.schema
                        .validate_node(node_index, &node.attributes, None)?;
                }

                Ok(())
            })
            .collect::<Result<Vec<_>, MedRecordError>>();

        if let Err(error) = result {
            self.schema = old_schema;

            return Err(error);
        }

        let result = self
            .graph
            .edges
            .iter()
            .map(|(edge_index, edge)| {
                let groups_of_edge = self
                    .groups_of_edge(edge_index)
                    .expect("groups of edge must exist")
                    .collect::<Vec<_>>();

                if !groups_of_edge.is_empty() {
                    for group in groups_of_edge {
                        self.schema
                            .validate_edge(edge_index, &edge.attributes, Some(group))?;
                    }
                } else {
                    self.schema
                        .validate_edge(edge_index, &edge.attributes, None)?;
                }

                Ok(())
            })
            .collect::<Result<Vec<_>, MedRecordError>>();

        if let Err(error) = result {
            self.schema = old_schema;

            return Err(error);
        }

        Ok(())
    }

    pub fn get_schema(&self) -> &Schema {
        &self.schema
    }

    pub fn node_indices(&self) -> impl Iterator<Item = &NodeIndex> {
        self.graph.node_indices()
    }

    pub fn node_attributes(&self, node_index: &NodeIndex) -> Result<&Attributes, MedRecordError> {
        self.graph
            .node_attributes(node_index)
            .map_err(MedRecordError::from)
    }

    pub fn node_attributes_mut(
        &mut self,
        node_index: &NodeIndex,
    ) -> Result<&mut Attributes, MedRecordError> {
        self.graph
            .node_attributes_mut(node_index)
            .map_err(MedRecordError::from)
    }

    pub fn outgoing_edges(
        &self,
        node_index: &NodeIndex,
    ) -> Result<impl Iterator<Item = &EdgeIndex>, MedRecordError> {
        self.graph
            .outgoing_edges(node_index)
            .map_err(MedRecordError::from)
    }

    pub fn incoming_edges(
        &self,
        node_index: &NodeIndex,
    ) -> Result<impl Iterator<Item = &EdgeIndex>, MedRecordError> {
        self.graph
            .incoming_edges(node_index)
            .map_err(MedRecordError::from)
    }

    pub fn edge_indices(&self) -> impl Iterator<Item = &EdgeIndex> {
        self.graph.edge_indices()
    }

    pub fn edge_attributes(&self, edge_index: &EdgeIndex) -> Result<&Attributes, MedRecordError> {
        self.graph
            .edge_attributes(edge_index)
            .map_err(MedRecordError::from)
    }

    pub fn edge_attributes_mut(
        &mut self,
        edge_index: &EdgeIndex,
    ) -> Result<&mut Attributes, MedRecordError> {
        self.graph
            .edge_attributes_mut(edge_index)
            .map_err(MedRecordError::from)
    }

    pub fn edge_endpoints(
        &self,
        edge_index: &EdgeIndex,
    ) -> Result<(&NodeIndex, &NodeIndex), MedRecordError> {
        self.graph
            .edge_endpoints(edge_index)
            .map_err(MedRecordError::from)
    }

    pub fn edges_connecting<'a>(
        &'a self,
        outgoing_node_indices: Vec<&'a NodeIndex>,
        incoming_node_indices: Vec<&'a NodeIndex>,
    ) -> impl Iterator<Item = &'a EdgeIndex> + 'a {
        self.graph
            .edges_connecting(outgoing_node_indices, incoming_node_indices)
    }

    pub fn edges_connecting_undirected<'a>(
        &'a self,
        first_node_indices: Vec<&'a NodeIndex>,
        second_node_indices: Vec<&'a NodeIndex>,
    ) -> impl Iterator<Item = &'a EdgeIndex> + 'a {
        self.graph
            .edges_connecting_undirected(first_node_indices, second_node_indices)
    }

    pub fn add_node(
        &mut self,
        node_index: NodeIndex,
        attributes: Attributes,
    ) -> Result<(), MedRecordError> {
        self.schema.validate_node(&node_index, &attributes, None)?;

        self.graph
            .add_node(node_index, attributes)
            .map_err(MedRecordError::from)
    }

    pub fn remove_node(&mut self, node_index: &NodeIndex) -> Result<Attributes, MedRecordError> {
        self.group_mapping.remove_node(node_index);

        self.graph
            .remove_node(node_index, &mut self.group_mapping)
            .map_err(MedRecordError::from)
    }

    pub fn add_nodes(&mut self, nodes: Vec<(NodeIndex, Attributes)>) -> Result<(), MedRecordError> {
        for (node_index, attributes) in nodes.into_iter() {
            self.add_node(node_index, attributes)?;
        }

        Ok(())
    }

    pub fn add_nodes_dataframes(
        &mut self,
        nodes_dataframes: impl IntoIterator<Item = impl Into<NodeDataFrameInput>>,
    ) -> Result<(), MedRecordError> {
        let nodes = nodes_dataframes
            .into_iter()
            .map(|dataframe_input| {
                let dataframe_input = dataframe_input.into();

                dataframe_to_nodes(dataframe_input.dataframe, &dataframe_input.index_column)
            })
            .collect::<Result<Vec<_>, _>>()?
            .into_iter()
            .flatten()
            .collect();

        self.add_nodes(nodes)
    }

    pub fn add_edge(
        &mut self,
        source_node_index: NodeIndex,
        target_node_index: NodeIndex,
        attributes: Attributes,
    ) -> Result<EdgeIndex, MedRecordError> {
        let edge_index = self
            .graph
            .add_edge(source_node_index, target_node_index, attributes.to_owned())
            .map_err(MedRecordError::from)?;

        match self.schema.validate_edge(&edge_index, &attributes, None) {
            Ok(()) => Ok(edge_index),
            Err(e) => {
                self.graph
                    .remove_edge(&edge_index)
                    .expect("Edge must exist");

                Err(e.into())
            }
        }
    }

    pub fn remove_edge(&mut self, edge_index: &EdgeIndex) -> Result<Attributes, MedRecordError> {
        self.group_mapping.remove_edge(edge_index);

        self.graph
            .remove_edge(edge_index)
            .map_err(MedRecordError::from)
    }

    pub fn add_edges(
        &mut self,
        edges: Vec<(NodeIndex, NodeIndex, Attributes)>,
    ) -> Result<Vec<EdgeIndex>, MedRecordError> {
        edges
            .into_iter()
            .map(|(source_edge_index, target_node_index, attributes)| {
                self.add_edge(source_edge_index, target_node_index, attributes)
            })
            .collect()
    }

    pub fn add_edges_dataframes(
        &mut self,
        edges_dataframes: impl IntoIterator<Item = impl Into<EdgeDataFrameInput>>,
    ) -> Result<Vec<EdgeIndex>, MedRecordError> {
        let edges = edges_dataframes
            .into_iter()
            .map(|dataframe_input| {
                let dataframe_input = dataframe_input.into();

                dataframe_to_edges(
                    dataframe_input.dataframe,
                    &dataframe_input.source_index_column,
                    &dataframe_input.target_index_column,
                )
            })
            .collect::<Result<Vec<_>, _>>()?
            .into_iter()
            .flatten()
            .collect();

        self.add_edges(edges)
    }

    pub fn add_group(
        &mut self,
        group: Group,
        node_indices: Option<Vec<NodeIndex>>,
        edge_indices: Option<Vec<EdgeIndex>>,
    ) -> Result<(), MedRecordError> {
        match (node_indices, edge_indices) {
            (None, None) => {
                self.group_mapping.add_group(group.clone(), None, None)?;

                Ok(())
            }
            (None, Some(edge_indices)) => {
                // Check that the edge_indices that are about to be added are actually in the graph
                for edge_index in &edge_indices {
                    if !self.graph.contains_edge(edge_index) {
                        return Err(MedRecordError::IndexError(format!(
                            "Cannot find edge with index {}",
                            edge_index,
                        )));
                    }
                }

                self.group_mapping
                    .add_group(group, None, Some(edge_indices))
            }
            (Some(node_indices), None) => {
                // Check that the node_indices that are about to be added are actually in the graph
                for node_index in &node_indices {
                    if !self.graph.contains_node(node_index) {
                        return Err(MedRecordError::IndexError(format!(
                            "Cannot find node with index {}",
                            node_index,
                        )));
                    }
                }

                self.group_mapping
                    .add_group(group, Some(node_indices), None)
            }
            (Some(node_indices), Some(edge_indices)) => {
                // Check that the node_indices that are about to be added are actually in the graph
                for node_index in &node_indices {
                    if !self.graph.contains_node(node_index) {
                        return Err(MedRecordError::IndexError(format!(
                            "Cannot find node with index {}",
                            node_index,
                        )));
                    }
                }

                // Check that the edge_indices that are about to be added are actually in the graph
                for edge_index in &edge_indices {
                    if !self.graph.contains_edge(edge_index) {
                        return Err(MedRecordError::IndexError(format!(
                            "Cannot find edge with index {}",
                            edge_index,
                        )));
                    }
                }

                self.group_mapping
                    .add_group(group, Some(node_indices), Some(edge_indices))
            }
        }
    }

    pub fn remove_group(&mut self, group: &Group) -> Result<(), MedRecordError> {
        self.group_mapping.remove_group(group)
    }

    pub fn add_node_to_group(
        &mut self,
        group: Group,
        node_index: NodeIndex,
    ) -> Result<(), MedRecordError> {
        let node_attributes = self.graph.node_attributes(&node_index)?;

        self.schema
            .validate_node(&node_index, node_attributes, Some(&group))?;

        self.group_mapping.add_node_to_group(group, node_index)
    }

    pub fn add_edge_to_group(
        &mut self,
        group: Group,
        edge_index: EdgeIndex,
    ) -> Result<(), MedRecordError> {
        let edge_attributes = self.graph.edge_attributes(&edge_index)?;

        self.schema
            .validate_edge(&edge_index, edge_attributes, Some(&group))?;

        self.group_mapping.add_edge_to_group(group, edge_index)
    }

    pub fn remove_node_from_group(
        &mut self,
        group: &Group,
        node_index: &NodeIndex,
    ) -> Result<(), MedRecordError> {
        if !self.graph.contains_node(node_index) {
            return Err(MedRecordError::IndexError(format!(
                "Cannot find node with index {}",
                node_index,
            )));
        }

        self.group_mapping.remove_node_from_group(group, node_index)
    }

    pub fn remove_edge_from_group(
        &mut self,
        group: &Group,
        edge_index: &EdgeIndex,
    ) -> Result<(), MedRecordError> {
        if !self.graph.contains_edge(edge_index) {
            return Err(MedRecordError::IndexError(format!(
                "Cannot find edge with index {}",
                edge_index,
            )));
        }

        self.group_mapping.remove_edge_from_group(group, edge_index)
    }

    pub fn groups(&self) -> impl Iterator<Item = &Group> {
        self.group_mapping.groups()
    }

    pub fn nodes_in_group(
        &self,
        group: &Group,
    ) -> Result<impl Iterator<Item = &NodeIndex>, MedRecordError> {
        self.group_mapping.nodes_in_group(group)
    }

    pub fn edges_in_group(
        &self,
        group: &Group,
    ) -> Result<impl Iterator<Item = &EdgeIndex>, MedRecordError> {
        self.group_mapping.edges_in_group(group)
    }

    pub fn groups_of_node(
        &self,
        node_index: &NodeIndex,
    ) -> Result<impl Iterator<Item = &Group>, MedRecordError> {
        if !self.graph.contains_node(node_index) {
            return Err(MedRecordError::IndexError(format!(
                "Cannot find node with index {}",
                node_index,
            )));
        }

        Ok(self.group_mapping.groups_of_node(node_index))
    }

    pub fn groups_of_edge(
        &self,
        edge_index: &EdgeIndex,
    ) -> Result<impl Iterator<Item = &Group>, MedRecordError> {
        if !self.graph.contains_edge(edge_index) {
            return Err(MedRecordError::IndexError(format!(
                "Cannot find edge with index {}",
                edge_index,
            )));
        }

        Ok(self.group_mapping.groups_of_edge(edge_index))
    }

    pub fn node_count(&self) -> usize {
        self.graph.node_count()
    }

    pub fn edge_count(&self) -> usize {
        self.graph.edge_count()
    }

    pub fn group_count(&self) -> usize {
        self.group_mapping.group_count()
    }

    pub fn contains_node(&self, node_index: &NodeIndex) -> bool {
        self.graph.contains_node(node_index)
    }

    pub fn contains_edge(&self, edge_index: &EdgeIndex) -> bool {
        self.graph.contains_edge(edge_index)
    }

    pub fn contains_group(&self, group: &Group) -> bool {
        self.group_mapping.contains_group(group)
    }

    pub fn neighbors_outgoing(
        &self,
        node_index: &NodeIndex,
    ) -> Result<impl Iterator<Item = &NodeIndex>, MedRecordError> {
        self.graph
            .neighbors_outgoing(node_index)
            .map_err(MedRecordError::from)
    }

    // TODO: Add tests
    pub fn neighbors_incoming(
        &self,
        node_index: &NodeIndex,
    ) -> Result<impl Iterator<Item = &NodeIndex>, MedRecordError> {
        self.graph
            .neighbors_incoming(node_index)
            .map_err(MedRecordError::from)
    }

    pub fn neighbors_undirected(
        &self,
        node_index: &NodeIndex,
    ) -> Result<impl Iterator<Item = &NodeIndex>, MedRecordError> {
        self.graph
            .neighbors_undirected(node_index)
            .map_err(MedRecordError::from)
    }

    pub fn clear(&mut self) {
        self.graph.clear();
        self.group_mapping.clear();
    }

    pub fn select_nodes<Q>(&self, query: Q) -> NodeSelection
    where
        Q: FnOnce(&mut Wrapper<NodeOperand>),
    {
        NodeSelection::new(self, query)
    }

    pub fn select_edges<Q>(&self, query: Q) -> EdgeSelection
    where
        Q: FnOnce(&mut Wrapper<EdgeOperand>),
    {
        EdgeSelection::new(self, query)
    }
}

impl Default for MedRecord {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod test {
    use super::{
        Attributes, DataType, GroupSchema, MedRecord, MedRecordAttribute, NodeIndex, Schema,
    };
    use crate::errors::MedRecordError;
    use polars::prelude::{DataFrame, NamedFrom, PolarsError, Series};
    use std::{collections::HashMap, fs};

    fn create_nodes() -> Vec<(NodeIndex, Attributes)> {
        vec![
            (
                "0".into(),
                HashMap::from([("lorem".into(), "ipsum".into())]),
            ),
            (
                "1".into(),
                HashMap::from([("amet".into(), "consectetur".into())]),
            ),
            (
                "2".into(),
                HashMap::from([("adipiscing".into(), "elit".into())]),
            ),
            ("3".into(), HashMap::new()),
        ]
    }

    fn create_edges() -> Vec<(NodeIndex, NodeIndex, Attributes)> {
        vec![
            (
                "0".into(),
                "1".into(),
                HashMap::from([
                    ("sed".into(), "do".into()),
                    ("eiusmod".into(), "tempor".into()),
                ]),
            ),
            (
                "1".into(),
                "0".into(),
                HashMap::from([
                    ("sed".into(), "do".into()),
                    ("eiusmod".into(), "tempor".into()),
                ]),
            ),
            (
                "1".into(),
                "2".into(),
                HashMap::from([("incididunt".into(), "ut".into())]),
            ),
            ("0".into(), "2".into(), HashMap::new()),
        ]
    }

    fn create_nodes_dataframe() -> Result<DataFrame, PolarsError> {
        let s0 = Series::new("index".into(), &["0", "1"]);
        let s1 = Series::new("attribute".into(), &[1, 2]);
        DataFrame::new(vec![s0.into(), s1.into()])
    }

    fn create_edges_dataframe() -> Result<DataFrame, PolarsError> {
        let s0 = Series::new("from".into(), &["0", "1"]);
        let s1 = Series::new("to".into(), &["1", "0"]);
        let s2 = Series::new("attribute".into(), &[1, 2]);
        DataFrame::new(vec![s0.into(), s1.into(), s2.into()])
    }

    fn create_medrecord() -> MedRecord {
        let nodes = create_nodes();
        let edges = create_edges();

        MedRecord::from_tuples(nodes, Some(edges), None).unwrap()
    }

    #[test]
    fn test_schema() {
        let schema = Schema {
            groups: HashMap::from([(
                "group".into(),
                GroupSchema {
                    nodes: HashMap::from([("attribute2".into(), DataType::Int.into())]),
                    edges: HashMap::from([("attribute2".into(), DataType::Int.into())]),
                    strict: None,
                },
            )]),
            default: Some(GroupSchema {
                nodes: HashMap::from([("attribute".into(), DataType::Int.into())]),
                edges: HashMap::from([("attribute".into(), DataType::Int.into())]),
                strict: None,
            }),
            strict: None,
        };

        let mut medrecord = MedRecord::with_schema(schema.clone());
        medrecord.add_group("group".into(), None, None).unwrap();

        assert_eq!(schema, *medrecord.get_schema());

        assert!(medrecord
            .add_node("0".into(), HashMap::from([("attribute".into(), 1.into())]))
            .is_ok());

        assert!(medrecord
            .add_node(
                "1".into(),
                HashMap::from([("attribute".into(), "1".into())])
            )
            .is_err_and(|e| matches!(e, MedRecordError::SchemaError(_))));

        medrecord
            .add_node(
                "1".into(),
                HashMap::from([
                    ("attribute".into(), 1.into()),
                    ("attribute2".into(), 1.into()),
                ]),
            )
            .unwrap();

        assert!(medrecord
            .add_node_to_group("group".into(), "1".into())
            .is_ok());

        medrecord
            .add_node(
                "2".into(),
                HashMap::from([
                    ("attribute".into(), 1.into()),
                    ("attribute2".into(), "1".into()),
                ]),
            )
            .unwrap();

        assert!(medrecord
            .add_node_to_group("group".into(), "2".into())
            .is_err_and(|e| { matches!(e, MedRecordError::SchemaError(_)) }));

        assert!(medrecord
            .add_edge(
                "0".into(),
                "1".into(),
                HashMap::from([("attribute".into(), 1.into())])
            )
            .is_ok());

        assert!(medrecord
            .add_edge(
                "0".into(),
                "1".into(),
                HashMap::from([("attribute".into(), "1".into())])
            )
            .is_err_and(|e| matches!(e, MedRecordError::SchemaError(_))));

        let edge_index = medrecord
            .add_edge(
                "0".into(),
                "1".into(),
                HashMap::from([
                    ("attribute".into(), 1.into()),
                    ("attribute2".into(), 1.into()),
                ]),
            )
            .unwrap();

        assert!(medrecord
            .add_edge_to_group("group".into(), edge_index)
            .is_ok());

        let edge_index = medrecord
            .add_edge(
                "0".into(),
                "1".into(),
                HashMap::from([
                    ("attribute".into(), 1.into()),
                    ("attribute2".into(), "1".into()),
                ]),
            )
            .unwrap();

        assert!(medrecord
            .add_edge_to_group("group".into(), edge_index)
            .is_err_and(|e| { matches!(e, MedRecordError::SchemaError(_)) }));
    }

    #[test]
    fn test_from_tuples() {
        let medrecord = create_medrecord();

        assert_eq!(4, medrecord.node_count());
        assert_eq!(4, medrecord.edge_count());
    }

    #[test]
    fn test_invalid_from_tuples() {
        let nodes = create_nodes();

        // Adding an edge pointing to a non-existing node should fail
        assert!(MedRecord::from_tuples(
            nodes.clone(),
            Some(vec![("0".into(), "50".into(), HashMap::new())]),
            None
        )
        .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Adding an edge from a non-existing should fail
        assert!(MedRecord::from_tuples(
            nodes,
            Some(vec![("50".into(), "0".into(), HashMap::new())]),
            None
        )
        .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_from_dataframes() {
        let nodes_dataframe = create_nodes_dataframe().unwrap();
        let edges_dataframe = create_edges_dataframe().unwrap();

        let medrecord = MedRecord::from_dataframes(
            vec![(nodes_dataframe, "index".to_string())],
            vec![(edges_dataframe, "from".to_string(), "to".to_string())],
            None,
        )
        .unwrap();

        assert_eq!(2, medrecord.node_count());
        assert_eq!(2, medrecord.edge_count());
    }

    #[test]
    fn test_from_nodes_dataframes() {
        let nodes_dataframe = create_nodes_dataframe().unwrap();

        let medrecord =
            MedRecord::from_nodes_dataframes(vec![(nodes_dataframe, "index".to_string())], None)
                .unwrap();

        assert_eq!(2, medrecord.node_count());
    }

    #[test]
    fn test_ron() {
        let medrecord = create_medrecord();

        let mut file_path = std::env::temp_dir().into_os_string();
        file_path.push("/medrecord_test/");

        fs::create_dir_all(&file_path).unwrap();

        file_path.push("test.ron");

        medrecord.to_ron(&file_path).unwrap();

        let loaded_medrecord = MedRecord::from_ron(&file_path).unwrap();

        assert_eq!(medrecord.node_count(), loaded_medrecord.node_count());
        assert_eq!(medrecord.edge_count(), loaded_medrecord.edge_count());
    }

    #[test]
    fn test_update_schema() {
        let mut medrecord = MedRecord::new();

        medrecord
            .add_node("0".into(), HashMap::from([("attribute".into(), 1.into())]))
            .unwrap();
        medrecord
            .add_node("1".into(), HashMap::from([("attribute".into(), 1.into())]))
            .unwrap();
        medrecord
            .add_edge(
                "0".into(),
                "1".into(),
                HashMap::from([("attribute".into(), 1.into())]),
            )
            .unwrap();

        let schema = Schema {
            groups: Default::default(),
            default: Some(GroupSchema {
                nodes: HashMap::from([("attribute".into(), DataType::Int.into())]),
                edges: HashMap::from([("attribute".into(), DataType::Int.into())]),
                strict: None,
            }),
            strict: None,
        };

        assert!(medrecord.update_schema(schema.clone()).is_ok());

        assert_eq!(schema, *medrecord.get_schema());
    }

    #[test]
    fn test_invalid_update_schema() {
        let mut medrecord = MedRecord::new();

        medrecord
            .add_node("0".into(), HashMap::from([("attribute2".into(), 1.into())]))
            .unwrap();

        let schema = Schema {
            groups: Default::default(),
            default: Some(GroupSchema {
                nodes: HashMap::from([("attribute".into(), DataType::Int.into())]),
                edges: HashMap::from([("attribute".into(), DataType::Int.into())]),
                strict: None,
            }),
            strict: None,
        };

        assert!(medrecord
            .update_schema(schema.clone())
            .is_err_and(|e| { matches!(e, MedRecordError::SchemaError(_)) }));

        assert_eq!(Schema::default(), *medrecord.get_schema());

        let mut medrecord = MedRecord::new();

        medrecord
            .add_node("0".into(), HashMap::from([("attribute".into(), 1.into())]))
            .unwrap();
        medrecord
            .add_node("1".into(), HashMap::from([("attribute".into(), 1.into())]))
            .unwrap();
        medrecord
            .add_edge(
                "0".into(),
                "1".into(),
                HashMap::from([("attribute2".into(), 1.into())]),
            )
            .unwrap();

        assert!(medrecord
            .update_schema(schema.clone())
            .is_err_and(|e| { matches!(e, MedRecordError::SchemaError(_)) }));

        assert_eq!(Schema::default(), *medrecord.get_schema());
    }

    #[test]
    fn test_node_indices() {
        let medrecord = create_medrecord();

        let node_indices = create_nodes()
            .into_iter()
            .map(|(node_index, _)| node_index)
            .collect::<Vec<_>>();

        for node_index in medrecord.node_indices() {
            assert!(node_indices.contains(node_index));
        }
    }

    #[test]
    fn test_node_attributes() {
        let medrecord = create_medrecord();

        let attributes = medrecord.node_attributes(&"0".into()).unwrap();

        assert_eq!(&create_nodes()[0].1, attributes);
    }

    #[test]
    fn test_invalid_node_attributes() {
        let medrecord = create_medrecord();

        // Querying a non-existing node should fail
        assert!(medrecord
            .node_attributes(&"50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_node_attributes_mut() {
        let mut medrecord = create_medrecord();

        let attributes = medrecord.node_attributes_mut(&"0".into()).unwrap();

        assert_eq!(&create_nodes()[0].1, attributes);

        let new_attributes = HashMap::from([("0".into(), "1".into()), ("2".into(), "3".into())]);

        attributes.clone_from(&new_attributes);

        assert_eq!(
            &new_attributes,
            medrecord.node_attributes(&"0".into()).unwrap()
        );
    }

    #[test]
    fn test_invalid_node_attributes_mut() {
        let mut medrecord = create_medrecord();

        // Accessing the node attributes of a non-existing node should fail
        assert!(medrecord
            .node_attributes_mut(&"50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_outgoing_edges() {
        let medrecord = create_medrecord();

        let edges = medrecord.outgoing_edges(&"0".into()).unwrap();

        assert_eq!(2, edges.count());
    }

    #[test]
    fn test_invalid_outgoing_edges() {
        let medrecord = create_medrecord();

        assert!(medrecord
            .outgoing_edges(&"50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))))
    }

    #[test]
    fn test_incoming_edges() {
        let medrecord = create_medrecord();

        let edges = medrecord.incoming_edges(&"2".into()).unwrap();

        assert_eq!(2, edges.count());
    }

    #[test]
    fn test_invalid_incoming_edges() {
        let medrecord = create_medrecord();

        assert!(medrecord
            .incoming_edges(&"50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))))
    }

    #[test]
    fn test_edge_indices() {
        let medrecord = create_medrecord();
        let edges = [0, 1, 2, 3];

        for edge in medrecord.edge_indices() {
            assert!(edges.contains(edge));
        }
    }

    #[test]
    fn test_edge_attributes() {
        let medrecord = create_medrecord();

        let attributes = medrecord.edge_attributes(&0).unwrap();

        assert_eq!(&create_edges()[0].2, attributes);
    }

    #[test]
    fn test_invalid_edge_attributes() {
        let medrecord = create_medrecord();

        // Querying a non-existing node should fail
        assert!(medrecord
            .edge_attributes(&50)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_edge_attributes_mut() {
        let mut medrecord = create_medrecord();

        let attributes = medrecord.edge_attributes_mut(&0).unwrap();

        assert_eq!(&create_edges()[0].2, attributes);

        let new_attributes = HashMap::from([("0".into(), "1".into()), ("2".into(), "3".into())]);

        attributes.clone_from(&new_attributes);

        assert_eq!(&new_attributes, medrecord.edge_attributes(&0).unwrap());
    }

    #[test]
    fn test_invalid_edge_attributes_mut() {
        let mut medrecord = create_medrecord();

        // Accessing the edge attributes of a non-existing edge should fail
        assert!(medrecord
            .edge_attributes_mut(&50)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_edge_endpoints() {
        let medrecord = create_medrecord();

        let edge = &create_edges()[0];

        let endpoints = medrecord.edge_endpoints(&0).unwrap();

        assert_eq!(&edge.0, endpoints.0);

        assert_eq!(&edge.1, endpoints.1);
    }

    #[test]
    fn test_invalid_edge_endpoints() {
        let medrecord = create_medrecord();

        // Accessing the edge endpoints of a non-existing edge should fail
        assert!(medrecord
            .edge_endpoints(&50)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_edges_connecting() {
        let medrecord = create_medrecord();

        let first_index = "0".into();
        let second_index = "1".into();
        let edges_connecting = medrecord.edges_connecting(vec![&first_index], vec![&second_index]);

        assert_eq!(vec![&0], edges_connecting.collect::<Vec<_>>());

        let first_index = "0".into();
        let second_index = "3".into();
        let edges_connecting = medrecord.edges_connecting(vec![&first_index], vec![&second_index]);

        assert_eq!(0, edges_connecting.count());

        let first_index = "0".into();
        let second_index = "1".into();
        let third_index = "2".into();
        let mut edges_connecting = medrecord
            .edges_connecting(vec![&first_index, &second_index], vec![&third_index])
            .collect::<Vec<_>>();

        edges_connecting.sort();
        assert_eq!(vec![&2, &3], edges_connecting);

        let first_index = "0".into();
        let second_index = "1".into();
        let third_index = "2".into();
        let fourth_index = "3".into();
        let mut edges_connecting = medrecord
            .edges_connecting(
                vec![&first_index, &second_index],
                vec![&third_index, &fourth_index],
            )
            .collect::<Vec<_>>();

        edges_connecting.sort();
        assert_eq!(vec![&2, &3], edges_connecting);
    }

    #[test]
    fn test_edges_connecting_undirected() {
        let medrecord = create_medrecord();

        let first_index = "0".into();
        let second_index = "1".into();
        let mut edges_connecting = medrecord
            .edges_connecting_undirected(vec![&first_index], vec![&second_index])
            .collect::<Vec<_>>();

        edges_connecting.sort();
        assert_eq!(vec![&0, &1], edges_connecting);
    }

    #[test]
    fn test_add_node() {
        let mut medrecord = MedRecord::new();

        assert_eq!(0, medrecord.node_count());

        medrecord.add_node("0".into(), HashMap::new()).unwrap();

        assert_eq!(1, medrecord.node_count());
    }
    #[test]
    fn test_invalid_add_node() {
        let mut graph = create_medrecord();

        assert!(graph
            .add_node("0".into(), HashMap::new())
            .is_err_and(|e| matches!(e, MedRecordError::AssertionError(_))));
    }

    #[test]
    fn test_remove_node() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("group".into(), Some(vec!["0".into()]), Some(vec![0]))
            .unwrap();

        let nodes = create_nodes();

        assert_eq!(4, medrecord.node_count());
        assert_eq!(4, medrecord.edge_count());
        assert_eq!(
            1,
            medrecord.nodes_in_group(&("group".into())).unwrap().count()
        );
        assert_eq!(
            1,
            medrecord.edges_in_group(&("group".into())).unwrap().count()
        );

        assert_eq!(nodes[0].1, medrecord.remove_node(&"0".into()).unwrap());

        assert_eq!(3, medrecord.node_count());
        assert_eq!(1, medrecord.edge_count());
        assert_eq!(
            0,
            medrecord.nodes_in_group(&("group".into())).unwrap().count()
        );
        assert_eq!(
            0,
            medrecord.edges_in_group(&("group".into())).unwrap().count()
        );
    }

    #[test]
    fn test_invalid_remove_node() {
        let mut medrecord = create_medrecord();

        // Removing a non-existing node should fail
        assert!(medrecord
            .remove_node(&"50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_add_nodes() {
        let mut medrecord = MedRecord::new();

        assert_eq!(0, medrecord.node_count());

        let nodes = create_nodes();

        medrecord.add_nodes(nodes).unwrap();

        assert_eq!(4, medrecord.node_count());
    }

    #[test]
    fn test_invalid_add_nodes() {
        let mut medrecord = create_medrecord();

        let nodes = create_nodes();

        assert!(medrecord
            .add_nodes(nodes)
            .is_err_and(|e| matches!(e, MedRecordError::AssertionError(_))));
    }

    #[test]
    fn test_add_nodes_dataframe() {
        let mut medrecord = MedRecord::new();

        assert_eq!(0, medrecord.node_count());

        let nodes_dataframe = create_nodes_dataframe().unwrap();

        medrecord
            .add_nodes_dataframes(vec![(nodes_dataframe, "index".to_string())])
            .unwrap();

        assert_eq!(2, medrecord.node_count());
    }

    #[test]
    fn test_add_edge() {
        let mut medrecord = create_medrecord();

        assert_eq!(4, medrecord.edge_count());

        medrecord
            .add_edge("0".into(), "3".into(), HashMap::new())
            .unwrap();

        assert_eq!(5, medrecord.edge_count());
    }

    #[test]
    fn test_invalid_add_edge() {
        let mut medrecord = MedRecord::new();

        let nodes = create_nodes();

        medrecord.add_nodes(nodes).unwrap();

        // Adding an edge pointing to a non-existing node should fail
        assert!(medrecord
            .add_edge("0".into(), "50".into(), HashMap::new())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Adding an edge from a non-existing node should fail
        assert!(medrecord
            .add_edge("50".into(), "0".into(), HashMap::new())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_remove_edge() {
        let mut medrecod = create_medrecord();

        let edges = create_edges();

        assert_eq!(edges[0].2, medrecod.remove_edge(&0).unwrap());
    }

    #[test]
    fn test_invalid_remove_edge() {
        let mut medrecord = create_medrecord();

        // Removing a non-existing edge should fail
        assert!(medrecord
            .remove_edge(&50)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_add_edges() {
        let mut medrecord = MedRecord::new();

        let nodes = create_nodes();

        medrecord.add_nodes(nodes).unwrap();

        assert_eq!(0, medrecord.edge_count());

        let edges = create_edges();

        medrecord.add_edges(edges).unwrap();

        assert_eq!(4, medrecord.edge_count());
    }

    #[test]
    fn test_add_edges_dataframe() {
        let mut medrecord = MedRecord::new();

        let nodes = create_nodes();

        medrecord.add_nodes(nodes).unwrap();

        assert_eq!(0, medrecord.edge_count());

        let edges = create_edges_dataframe().unwrap();

        medrecord
            .add_edges_dataframes(vec![(edges, "from", "to")])
            .unwrap();

        assert_eq!(2, medrecord.edge_count());
    }

    #[test]
    fn test_add_group() {
        let mut medrecord = create_medrecord();

        assert_eq!(0, medrecord.group_count());

        medrecord.add_group("0".into(), None, None).unwrap();

        assert_eq!(1, medrecord.group_count());

        medrecord
            .add_group("1".into(), Some(vec!["0".into(), "1".into()]), None)
            .unwrap();

        assert_eq!(2, medrecord.group_count());

        assert_eq!(2, medrecord.nodes_in_group(&"1".into()).unwrap().count())
    }

    #[test]
    fn test_invalid_add_group() {
        let mut medrecord = create_medrecord();

        // Adding a group with a non-existing node should fail
        assert!(medrecord
            .add_group("0".into(), Some(vec!["50".into()]), None)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        medrecord.add_group("0".into(), None, None).unwrap();

        // Adding an already existing group should fail
        assert!(medrecord
            .add_group("0".into(), None, None)
            .is_err_and(|e| matches!(e, MedRecordError::AssertionError(_))));
    }

    #[test]
    fn test_remove_group() {
        let mut medrecord = create_medrecord();

        medrecord.add_group("0".into(), None, None).unwrap();

        assert_eq!(1, medrecord.group_count());

        medrecord.remove_group(&"0".into()).unwrap();

        assert_eq!(0, medrecord.group_count());
    }

    #[test]
    fn test_invalid_remove_group() {
        let mut medrecord = MedRecord::new();

        // Removing a non-existing group should fail
        assert!(medrecord
            .remove_group(&"0".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_add_node_to_group() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), Some(vec!["0".into(), "1".into()]), None)
            .unwrap();

        assert_eq!(2, medrecord.nodes_in_group(&"0".into()).unwrap().count());

        medrecord.add_node_to_group("0".into(), "2".into()).unwrap();

        assert_eq!(3, medrecord.nodes_in_group(&"0".into()).unwrap().count());
    }

    #[test]
    fn test_invalid_add_node_to_group() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), Some(vec!["0".into()]), None)
            .unwrap();

        // Adding to a non-existing group should fail
        assert!(medrecord
            .add_node_to_group("1".into(), "0".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Adding a non-existing node to a group should fail
        assert!(medrecord
            .add_node_to_group("0".into(), "50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Adding a node to a group that already is in the group should fail
        assert!(medrecord
            .add_node_to_group("0".into(), "0".into())
            .is_err_and(|e| matches!(e, MedRecordError::AssertionError(_))));
    }

    #[test]
    fn test_add_edge_to_group() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), None, Some(vec![0, 1]))
            .unwrap();

        assert_eq!(2, medrecord.edges_in_group(&"0".into()).unwrap().count());

        medrecord.add_edge_to_group("0".into(), 2).unwrap();

        assert_eq!(3, medrecord.edges_in_group(&"0".into()).unwrap().count());
    }

    #[test]
    fn test_invalid_add_edge_to_group() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), None, Some(vec![0]))
            .unwrap();

        // Adding to a non-existing group should fail
        assert!(medrecord
            .add_edge_to_group("1".into(), 0)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Adding a non-existing edge to a group should fail
        assert!(medrecord
            .add_edge_to_group("0".into(), 50)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Adding an edge to a group that already is in the group should fail
        assert!(medrecord
            .add_edge_to_group("0".into(), 0)
            .is_err_and(|e| matches!(e, MedRecordError::AssertionError(_))));
    }

    #[test]
    fn test_remove_node_from_group() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), Some(vec!["0".into(), "1".into()]), None)
            .unwrap();

        assert_eq!(2, medrecord.nodes_in_group(&"0".into()).unwrap().count());

        medrecord
            .remove_node_from_group(&"0".into(), &"0".into())
            .unwrap();

        assert_eq!(1, medrecord.nodes_in_group(&"0".into()).unwrap().count());
    }

    #[test]
    fn test_invalid_remove_node_from_group() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), Some(vec!["0".into()]), None)
            .unwrap();

        // Removing a node from a non-existing group should fail
        assert!(medrecord
            .remove_node_from_group(&"50".into(), &"0".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Removing a non-existing node from a group should fail
        assert!(medrecord
            .remove_node_from_group(&"0".into(), &"50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Removing a node from a group it is not in should fail
        assert!(medrecord
            .remove_node_from_group(&"0".into(), &"1".into())
            .is_err_and(|e| matches!(e, MedRecordError::AssertionError(_))));
    }

    #[test]
    fn test_remove_edge_from_group() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), None, Some(vec![0, 1]))
            .unwrap();

        assert_eq!(2, medrecord.edges_in_group(&"0".into()).unwrap().count());

        medrecord.remove_edge_from_group(&"0".into(), &0).unwrap();

        assert_eq!(1, medrecord.edges_in_group(&"0".into()).unwrap().count());
    }

    #[test]
    fn test_invalid_remove_edge_from_group() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), None, Some(vec![0]))
            .unwrap();

        // Removing an edge from a non-existing group should fail
        assert!(medrecord
            .remove_edge_from_group(&"50".into(), &0)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Removing a non-existing edge from a group should fail
        assert!(medrecord
            .remove_edge_from_group(&"0".into(), &50)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));

        // Removing an edge from a group it is not in should fail
        assert!(medrecord
            .remove_edge_from_group(&"0".into(), &1)
            .is_err_and(|e| matches!(e, MedRecordError::AssertionError(_))));
    }

    #[test]
    fn test_groups() {
        let mut medrecord = create_medrecord();

        medrecord.add_group("0".into(), None, None).unwrap();

        let groups = medrecord.groups().collect::<Vec<_>>();

        assert_eq!(vec![&(MedRecordAttribute::from("0"))], groups);
    }

    #[test]
    fn test_nodes_in_group() {
        let mut medrecord = create_medrecord();

        medrecord.add_group("0".into(), None, None).unwrap();

        assert_eq!(0, medrecord.nodes_in_group(&"0".into()).unwrap().count());

        medrecord
            .add_group("1".into(), Some(vec!["0".into()]), None)
            .unwrap();

        assert_eq!(1, medrecord.nodes_in_group(&"1".into()).unwrap().count());
    }

    #[test]
    fn test_invalid_nodes_in_group() {
        let medrecord = create_medrecord();

        // Querying a non-existing group should fail
        assert!(medrecord
            .nodes_in_group(&"0".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_edges_in_group() {
        let mut medrecord = create_medrecord();

        medrecord.add_group("0".into(), None, None).unwrap();

        assert_eq!(0, medrecord.edges_in_group(&"0".into()).unwrap().count());

        medrecord
            .add_group("1".into(), None, Some(vec![0]))
            .unwrap();

        assert_eq!(1, medrecord.edges_in_group(&"1".into()).unwrap().count());
    }

    #[test]
    fn test_invalid_edges_in_group() {
        let medrecord = create_medrecord();

        // Querying a non-existing group should fail
        assert!(medrecord
            .edges_in_group(&"0".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_groups_of_node() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), Some(vec!["0".into()]), None)
            .unwrap();

        assert_eq!(1, medrecord.groups_of_node(&"0".into()).unwrap().count());
    }

    #[test]
    fn test_invalid_groups_of_node() {
        let medrecord = create_medrecord();

        // Queyring the groups of a non-existing node should fail
        assert!(medrecord
            .groups_of_node(&"50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))))
    }

    #[test]
    fn test_groups_of_edge() {
        let mut medrecord = create_medrecord();

        medrecord
            .add_group("0".into(), None, Some(vec![0]))
            .unwrap();

        assert_eq!(1, medrecord.groups_of_edge(&0).unwrap().count());
    }

    #[test]
    fn test_invalid_groups_of_edge() {
        let medrecord = create_medrecord();

        // Queyring the groups of a non-existing edge should fail
        assert!(medrecord
            .groups_of_edge(&50)
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))))
    }

    #[test]
    fn test_node_count() {
        let mut medrecord = MedRecord::new();

        assert_eq!(0, medrecord.node_count());

        medrecord.add_node("0".into(), HashMap::new()).unwrap();

        assert_eq!(1, medrecord.node_count());
    }

    #[test]
    fn test_edge_count() {
        let mut medrecord = MedRecord::new();

        medrecord.add_node("0".into(), HashMap::new()).unwrap();
        medrecord.add_node("1".into(), HashMap::new()).unwrap();

        assert_eq!(0, medrecord.edge_count());

        medrecord
            .add_edge("0".into(), "1".into(), HashMap::new())
            .unwrap();

        assert_eq!(1, medrecord.edge_count());
    }

    #[test]
    fn test_group_count() {
        let mut medrecord = create_medrecord();

        assert_eq!(0, medrecord.group_count());

        medrecord.add_group("0".into(), None, None).unwrap();

        assert_eq!(1, medrecord.group_count());
    }

    #[test]
    fn test_contains_node() {
        let medrecord = create_medrecord();

        assert!(medrecord.contains_node(&"0".into()));

        assert!(!medrecord.contains_node(&"50".into()));
    }

    #[test]
    fn test_contains_edge() {
        let medrecord = create_medrecord();

        assert!(medrecord.contains_edge(&0));

        assert!(!medrecord.contains_edge(&50));
    }

    #[test]
    fn test_contains_group() {
        let mut medrecord = create_medrecord();

        assert!(!medrecord.contains_group(&"0".into()));

        medrecord.add_group("0".into(), None, None).unwrap();

        assert!(medrecord.contains_group(&"0".into()));
    }

    #[test]
    fn test_neighbors() {
        let medrecord = create_medrecord();

        let neighbors = medrecord.neighbors_outgoing(&"0".into()).unwrap();

        assert_eq!(2, neighbors.count());
    }

    #[test]
    fn test_invalid_neighbors() {
        let medrecord = MedRecord::new();

        // Querying neighbors of a non-existing node sohuld fail
        assert!(medrecord
            .neighbors_outgoing(&"0".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_neighbors_undirected() {
        let medrecord = create_medrecord();

        let neighbors = medrecord.neighbors_outgoing(&"2".into()).unwrap();
        assert_eq!(0, neighbors.count());

        let neighbors = medrecord.neighbors_undirected(&"2".into()).unwrap();
        assert_eq!(2, neighbors.count());
    }

    #[test]
    fn test_invalid_neighbors_undirected() {
        let medrecord = create_medrecord();

        assert!(medrecord
            .neighbors_undirected(&"50".into())
            .is_err_and(|e| matches!(e, MedRecordError::IndexError(_))));
    }

    #[test]
    fn test_clear() {
        let mut medrecord = create_medrecord();

        medrecord.clear();

        assert_eq!(0, medrecord.node_count());
        assert_eq!(0, medrecord.edge_count());
        assert_eq!(0, medrecord.group_count());
    }
}
