import torch.nn as nn

### EXPERIMENTAL ###

class MultiLayerPerceptron(nn.Module):
    """
    MultiLayerPerceptron is a neural network module implementing a customizable feedforward
    fully connected network.

    This class facilitates the creation of a multi-layer perceptron with a user-defined number of
    hidden layers, activation function, and an optional scaling factor for the inputs. The network
    can be used in various deep learning applications requiring a fully connected architecture.

    :ivar input_scale: The scaling factor applied to the input before passing it through the network.
    :type input_scale: float
    :ivar layers: A sequential container holding all the layers of the neural network.
    :type layers: torch.nn.Sequential
    """

    def __init__(self, input_dim, hidden_layers, activation, input_scale=1.0, seed=None):
        super(MultiLayerPerceptron, self).__init__()
        if seed is not None:
            torch.manual_seed(seed)

        self.input_scale = input_scale

        layers = []
        prev_layer_size = input_dim
        for current_layer_size in hidden_layers:
            layer = nn.Linear(prev_layer_size, current_layer_size)
            nn.init.normal_(layer.weight, mean=0.0, std=1.0)  # Initialize weights with N(0, 1)
            # nn.init.constant_(layer.bias, 0.0)  # Optional: Initialize biases to 0
            layers.append(layer)
            if isinstance(activation, nn.Module):
                layers.append(activation)  # Use the activation layer directly
            else:
                layers.append(nn.ReLU())  # Fallback to ReLU if a function is passed
            prev_layer_size = current_layer_size

        # Add the output layer (no activation)
        output_layer = nn.Linear(prev_layer_size, 1)
        nn.init.normal_(output_layer.weight, mean=0.0, std=1.0)  # Initialize output layer weights
        nn.init.constant_(output_layer.bias, 0.0)  # Optional: Initialize biases to 0
        layers.append(output_layer)

        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        scaled_input = self.scale_input(x)
        return self.layers(scaled_input)

    def scale_input(self, x):
        return x * self.input_scale


import numpy as np

import torch
import torch.nn as nn
import networkx as nx


class CausalPerceptronNetwork:
    """
    CausalPerceptronNetwork

    Neural network model for generating synthetic data based on a directed acyclic
    graph (DAG). This class models causal relationships defined within the DAG
    structure, associates each node in the graph with a multi-layer perceptron
    (MLP), and generates synthetic datasets by traversing the DAG in topological
    order. It allows for parallelized computations on GPUs for enhanced performance.

    The network uses customizable parameters such as the number of samples, hidden
    layer dimensions, activation functions, input scaling, and noise distributions.
    The generated data can be rescaled to a specified numeric range.

    Zhang, K., Wang, Z., Zhang, J., & Schölkopf, B. (2015). On estimation of functional
    causal models: general results and application to the post-nonlinear causal model.
    ACM Transactions on Intelligent Systems and Technology (TIST), 7(2), 1-22.

    Goudet, O., Kalainathan, D., Caillou, P., Guyon, I., Lopez-Paz, D., & Sebag, M. (2018).
    Learning functional causal models with generative neural networks. Explainable and
    interpretable models in computer vision and machine learning, 39-80.

    :ivar graph: The directed acyclic graph (DAG) defining causal dependencies.
    :type graph: nx.DiGraph
    :ivar num_samples: Number of samples to generate.
    :type num_samples: int
    :ivar noise_distribution: Function to generate noise samples.
    :type noise_distribution: Callable
    :ivar rescale_min: Minimum value for rescaling generated data.
    :type rescale_min: float
    :ivar rescale_max: Maximum value for rescaling generated data.
    :type rescale_max: float
    :ivar hidden_dimensions: List specifying dimensions of hidden layers.
    :type hidden_dimensions: List[int]
    :ivar input_scale: Scaling factor for the inputs.
    :type input_scale: float
    :ivar activation_function: Activation function for layers; default is ReLU.
    :type activation_function: Module
    :ivar node_to_mlp: Dictionary mapping each graph node to its corresponding MLP.
    :type node_to_mlp: dict
    :ivar parallelize: Whether to enable multi-GPU data parallelism.
    :type parallelize: bool
    :ivar device: Computation device (e.g., "cuda" for GPU, "cpu").
    :type device: torch.device
    """

    def __init__(self, graph, num_samples, noise_distribution, rescale_min, rescale_max, hidden_dimensions=None,
                 input_scale=5, activation_module=nn.ReLU(), parallelize=False, device="cuda"):
        if not self.is_acyclic(graph):
            raise ValueError("Graph contains cycles.")

        if num_samples < 1:
            raise ValueError("Number of samples must be positive.")

        if rescale_min > rescale_max:
            raise ValueError("Rescale min must be less than or equal to rescale max.")

        if input_scale <= 0:
            raise ValueError("Input scale must be positive.")

        if hidden_dimensions is None:
            hidden_dimensions = [10]

        if any(dim < 1 for dim in hidden_dimensions):
            raise ValueError("Hidden dimensions must be positive.")

        self.graph = graph
        self.num_samples = num_samples
        self.noise_distribution = noise_distribution
        self.rescale_min = rescale_min
        self.rescale_max = rescale_max
        self.hidden_dimensions = hidden_dimensions
        self.input_scale = input_scale
        self.activation_function = activation_module
        self.node_to_mlp = {}
        self.parallelize = parallelize
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")

        # Initialize an MLP for each node
        for node in self.graph.nodes:
            input_dim = len(list(graph.predecessors(node))) + 1  # Parents + noise input
            mlp = MultiLayerPerceptron(
                input_dim=input_dim,
                hidden_layers=self.hidden_dimensions,
                activation=self.activation_function,
                input_scale=self.input_scale
            )

            # Parallelize the MLP if requested
            if self.parallelize and torch.cuda.device_count() > 1:
                mlp = nn.DataParallel(mlp)

            mlp.to(self.device)  # Move model to device
            self.initialize_weights(mlp)  # Apply weight initialization
            self.node_to_mlp[node] = mlp

    def generate_data(self):
        """
        Generate synthetic data based on the DAG structure.

        Returns:
            np.ndarray: Generated dataset of shape (num_samples, num_nodes).
        """
        nodes = list(self.graph.nodes)
        node_to_index = {node: i for i, node in enumerate(nodes)}
        valid_order = self.topological_sort(self.graph)

        # Initialize the data array
        data = torch.zeros((self.num_samples, len(nodes)), device=self.device)

        for node in valid_order:
            parents = list(self.graph.predecessors(node))
            mlp = self.node_to_mlp[node]

            # Prepare inputs for the MLP
            parent_indices = [node_to_index[parent] for parent in parents]
            parent_data = data[:, parent_indices]  # Shape: (num_samples, len(parents))
            noise = torch.tensor(self.noise_distribution((self.num_samples, 1)), dtype=torch.float32,
                                 device=self.device)

            # Combine parent data and noise
            inputs = torch.cat((parent_data, noise), dim=1)

            # Pass inputs through the MLP
            node_data = mlp(inputs).squeeze()

            # Rescale the data
            if self.rescale_min < self.rescale_max:
                node_data = self.rescale_data(node_data)

            # Store the generated data for this node
            data[:, node_to_index[node]] = node_data

        return data.cpu().detach().numpy()

    def rescale_data(self, column, epsilon=1e-8):
        """
        Rescale a data column to the specified range [rescale_min, rescale_max].
        """
        col_min, col_max = column.min(), column.max()
        if col_max - col_min > epsilon:
            return self.rescale_min + (column - col_min) * (self.rescale_max - self.rescale_min) / (col_max - col_min)
        return column

    @staticmethod
    def initialize_weights(mlp):
        """
        Initialize the weights of an MLP using Xavier initialization for weights
        and constant initialization for biases.
        """
        for layer in mlp.layers:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.constant_(layer.bias, 0.1)

    @staticmethod
    def is_acyclic(graph):
        return nx.is_directed_acyclic_graph(graph)

    @staticmethod
    def topological_sort(graph):
        return list(nx.topological_sort(graph))
