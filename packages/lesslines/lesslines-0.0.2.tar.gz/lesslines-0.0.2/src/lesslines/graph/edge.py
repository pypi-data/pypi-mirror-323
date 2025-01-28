class Edge:
    """
    Represents an edge in the graph.
    Edges connect two nodes and can have associated properties such as weight or type.

    Attributes:
        start_node (Node): The starting node of the edge.
        end_node (Node): The ending node of the edge.
        weight (float): The weight or cost associated with the edge.
        metadata (dict): Additional information about the edge.
    """

    def __init__(self, start_node, end_node, weight=1.0, metadata=None):
        """
        Initialize an Edge instance.
        
        Args:
            start_node (Node): The starting node of the edge.
            end_node (Node): The ending node of the edge.
            weight (float, optional): The weight or cost associated with the edge (default is 1.0).
            metadata (dict, optional): Additional information about the edge.
        """
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
        self.metadata = metadata or {}

    def __repr__(self):
        """
        Return a string representation of the Edge instance.

        Returns:
            str: A string showing the start node, end node, and weight.
        """
        return (f"Edge(start_node={self.start_node.node_id}, "
                f"end_node={self.end_node.node_id}, weight={self.weight})")

    def add_metadata(self, key, value):
        """
        Add or update metadata for the edge.

        Args:
            key (str): The key for the metadata.
            value (Any): The value associated with the key.
        """
        self.metadata[key] = value
