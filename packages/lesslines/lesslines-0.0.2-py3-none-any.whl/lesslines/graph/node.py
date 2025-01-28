class Node:
    """
    Represents a node in the graph.
    Nodes can act as junctions, cities, or rest areas.

    Attributes:
        node_id (str): A unique identifier for the node.
        label (str, optional): A human-readable label for the node.
        metadata (dict): Additional information about the node.
    """

    def __init__(self, node_id, label=None, metadata=None):
        """
        Initialize a Node instance.
        
        Args:
            node_id (str): A unique identifier for the node.
            label (str, optional): A human-readable label for the node.
            metadata (dict, optional): Additional information about the node.
        """
        self.node_id = node_id
        self.label = label
        self.metadata = metadata or {}

    def __repr__(self):
        """
        Return a string representation of the Node instance.

        Returns:
            str: A string showing the node_id and label.
        """
        return f"Node(node_id='{self.node_id}', label='{self.label}')"

    def add_metadata(self, key, value):
        """
        Add or update metadata for the node.

        Args:
            key (str): The key for the metadata.
            value (Any): The value associated with the key.
        """
        self.metadata[key] = value
