class Network:
    """
    Represents a graph-based network consisting of nodes and edges.

    Attributes:
        network_id (str): A unique identifier for the network.
        nodes (dict): A dictionary mapping node IDs to Node objects.
        edges (list): A list of all Edge objects in the network.
    """

    def __init__(self, network_id):
        """
        Initialize a Network instance.

        Args:
            network_id (str): A unique identifier for the network.
        """
        self.network_id = network_id
        self.nodes = {}  # Dictionary to store nodes with their IDs as keys
        self.edges = []  # List to store all edges

    def add_node(self, node):
        """
        Add a node to the network.

        Args:
            node (Node): The Node object to add to the network.

        Raises:
            ValueError: If a node with the same ID already exists in the network.
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node with ID '{node.node_id}' already exists in the network.")
        self.nodes[node.node_id] = node

    def add_edge(self, edge):
        """
        Add an edge to the network.

        Args:
            edge (Edge): The Edge object to add to the network.

        Raises:
            ValueError: If either the start or end node of the edge is not in the network.
        """
        if edge.start_node.node_id not in self.nodes or edge.end_node.node_id not in self.nodes:
            raise ValueError("Both start and end nodes of the edge must exist in the network.")
        self.edges.append(edge)

    def get_neighbors(self, node_id):
        """
        Get all neighboring nodes connected to a given node.

        Args:
            node_id (str): The ID of the node whose neighbors are to be found.

        Returns:
            list: A list of Node objects that are neighbors of the given node.

        Raises:
            ValueError: If the node with the specified ID does not exist in the network.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node with ID '{node_id}' does not exist in the network.")

        neighbors = []
        for edge in self.edges:
            if edge.start_node.node_id == node_id:
                neighbors.append(edge.end_node)
            elif edge.end_node.node_id == node_id:
                neighbors.append(edge.start_node)
        return neighbors

    def remove_node(self, node_id):
        """
        Remove a node and all associated edges from the network.

        Args:
            node_id (str): The ID of the node to remove.

        Raises:
            ValueError: If the node with the specified ID does not exist in the network.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node with ID '{node_id}' does not exist in the network.")

        # Remove all edges connected to this node
        self.edges = [edge for edge in self.edges if edge.start_node.node_id != node_id and edge.end_node.node_id != node_id]
        # Remove the node itself
        del self.nodes[node_id]

    def remove_edge(self, edge):
        """
        Remove a specific edge from the network.

        Args:
            edge (Edge): The Edge object to remove.

        Raises:
            ValueError: If the specified edge does not exist in the network.
        """
        if edge not in self.edges:
            raise ValueError("The specified edge does not exist in the network.")
        self.edges.remove(edge)

    def __repr__(self):
        """
        Return a string representation of the Network instance.

        Returns:
            str: A string summarizing the network's ID, number of nodes, and edges.
        """
        return f"Network(network_id='{self.network_id}', nodes={len(self.nodes)}, edges={len(self.edges)})"
