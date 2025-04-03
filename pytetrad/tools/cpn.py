###
# This version uses PyTorch, in case we want later to learn the MLP weights.
###
from typing import Union, Tuple

import pandas as pd
import torch.nn as nn

class NoiseDistribution:
    def __init__(self, distribution_type="beta", **kwargs):
        """
        Initialize a noise distribution.

        Parameters:
        - distribution_type: str, the type of distribution ("beta", "normal", "uniform", etc.).
        - kwargs: parameters specific to the chosen distribution.
        """
        self.distribution_type = distribution_type
        self.params = kwargs

    def sample(self, size):
        """Generate samples from the stored distribution."""
        if self.distribution_type == "beta":
            return np.random.beta(self.params.get("alpha", 2), self.params.get("beta", 5), size)
        elif self.distribution_type == "normal":
            return np.random.normal(self.params.get("mean", 0), self.params.get("std", 1), size)
        elif self.distribution_type == "uniform":
            return np.random.uniform(self.params.get("low", 0), self.params.get("high", 1), size)
        else:
            raise ValueError(f"Unsupported distribution type: {self.distribution_type}")

    def __repr__(self):
        return f"NoiseDistribution(type={self.distribution_type}, params={self.params})"

class MultiLayerPerceptron(nn.Module):
    def __init__(self, input_dim: int, hidden_layers: list, activation: nn.Module,
                 variable_type: Union[str, Tuple[str, int]] = "continuous", input_scale: float = 1.0):
        """
        Args:
            input_dim (int): Number of input features.
            hidden_layers (list): List of integers specifying hidden layer sizes.
            activation (nn.Module): Activation function to use.
            variable_type (Union[str, Tuple[str, int]]): Variable type ("continuous", "binary", or ("multinomial", num_categories)).
            input_scale (float): Scaling factor for input.
        """
        super(MultiLayerPerceptron, self).__init__()

        # Validate variable_type
        if not isinstance(variable_type, (str, tuple)) or \
                (isinstance(variable_type, tuple) and (
                        len(variable_type) != 2 or not isinstance(variable_type[0], str) or not isinstance(
                    variable_type[1], int))):
            raise ValueError(
                "variable_type must be a string (e.g., 'continuous', 'binary') or a tuple (e.g., ('multinomial', 3)).")

        self.input_scale = input_scale
        self.variable_type = variable_type

        # Initialize layers as before
        layers = []
        prev_layer_size = input_dim
        for current_layer_size in hidden_layers:
            layer = nn.Linear(prev_layer_size, current_layer_size)
            nn.init.normal_(layer.weight, mean=0.0, std=1.0)  # Initialize weights with N(0, 1)
            layers.append(layer)
            layers.append(activation if isinstance(activation, nn.Module) else nn.ReLU())
            prev_layer_size = current_layer_size

        # Add output layer
        if variable_type == "continuous":
            layers.append(nn.Linear(prev_layer_size, 1))
        elif variable_type == "binary":
            layers.append(nn.Linear(prev_layer_size, 1))
            layers.append(nn.Sigmoid())
        elif isinstance(variable_type, tuple) and variable_type[0] == "multinomial":
            num_categories = variable_type[1]
            layers.append(nn.Linear(prev_layer_size, num_categories))
            layers.append(nn.Softmax(dim=-1))

        self.layers = nn.Sequential(*layers)

    def forward(self, x):
        scaled_input = self.scale_input(x)

        # Stabilize logits for Softmax
        if isinstance(self.variable_type, tuple) and self.variable_type[0] == "multinomial":
            logits = self.layers[:-1](scaled_input)  # Get logits without Softmax
            logits = logits - logits.max(dim=-1, keepdim=True).values  # Normalize logits for stability
            output = torch.softmax(logits, dim=-1)  # Apply Softmax manually
        else:
            output = self.layers(scaled_input)

        if self.variable_type == "binary":
            return torch.bernoulli(output)
        elif isinstance(self.variable_type, tuple) and self.variable_type[0] == "multinomial":
            return torch.multinomial(output, 1)
        return output

    def scale_input(self, x):
        x_scaled = x * self.input_scale
        # Optional: Standardize inputs to zero-mean, unit-variance
        return (x_scaled - x_scaled.mean(dim=0, keepdim=True)) / (x_scaled.std(dim=0, keepdim=True) + 1e-8)


import numpy as np

import torch.nn as nn

import torch

torch.set_default_dtype(torch.float64)

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

    :ivar graph: The directed acyclic graph (DAG) defining causal dependencies.
    :type graph: nx.DiGraph
    :ivar num_samples: Number of samples to generate.
    :type num_samples: int
    :ivar noise_distributions: A map from graph.getNodes() to Functions for generating noise samples.
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
    def __init__(self, graph, num_samples, noise_distributions, rescale_min=None, rescale_max=None,
                 hidden_dimensions=None, input_scale=1, activation_module=nn.ReLU(), nonlinearity='relu', parallelize=True,
                 device="cpu", discrete_prob=0, min_num_categories=2, max_num_categories=5, seed=None):
        # Set random seed for reproducibility
        if seed is not None:
            np.random.seed(seed)  # For NumPy-based operations
            torch.manual_seed(seed)  # For PyTorch-based operations
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)

        if not self.is_acyclic(graph):
            raise ValueError("Graph contains cycles.")

        if num_samples < 1:
            raise ValueError("Number of samples must be positive.")

        if rescale_min is not None and rescale_max is not None and rescale_min > rescale_max:
            rescale_min, rescale_max = rescale_max, rescale_min

        if input_scale <= 0:
            raise ValueError("Input scale must be positive.")

        if hidden_dimensions is None:
            hidden_dimensions = [10]

        if any(dim < 1 for dim in hidden_dimensions):
            raise ValueError("Hidden dimensions must be positive.")

        self.graph = graph
        self.num_samples = num_samples
        self.noise_distributions = noise_distributions
        self.rescale_min = rescale_min
        self.rescale_max = rescale_max
        self.hidden_dimensions = hidden_dimensions
        self.input_scale = input_scale
        self.activation_function = activation_module
        self.node_to_mlp = {}
        self.parallelize = parallelize
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.variable_types = {}
        self.nonlinearity = nonlinearity
        self.seed = seed  # Store the seed

        # Assign variable types to each node
        for node in self.graph.getNodes():
            if np.random.rand() < discrete_prob:
                num_categories = np.random.randint(min_num_categories, max_num_categories)  # Random number of categories between 2 and 4
                self.variable_types[node] = ("multinomial", num_categories)
            else:
                self.variable_types[node] = "continuous"

        # Initialize an MLP for each node
        for node in self.graph.getNodes():
            input_dim = len(list(graph.getParents(node))) + 1  # Parents + noise input
            mlp = MultiLayerPerceptron(
                input_dim=input_dim,
                hidden_layers=self.hidden_dimensions,
                activation=self.activation_function,
                input_scale=self.input_scale,
                variable_type=self.variable_types[node]
            )

            # Parallelize the MLP if requested
            if self.parallelize and torch.cuda.device_count() > 1:
                mlp = nn.DataParallel(mlp)

            # mlp.to(self.device)
            mlp.to(self.device).to(torch.float64) # Move model to the device
            self.initialize_weights(mlp, nonlinearity) # Apply weight initialization
            self.node_to_mlp[node] = mlp

    def generate_data(self):
        """
        Generate synthetic data based on the DAG structure.

        Returns:
            pd.DataFrame: Generated dataset as a Pandas DataFrame with appropriate dtypes.
        """
        nodes = list(self.graph.getNodes())
        node_to_index = {node: i for i, node in enumerate(nodes)}
        valid_order = self.topological_sort(self.graph)

        # Initialize the data array
        # data = torch.zeros((self.num_samples, len(nodes)), device=self.device)
        data = torch.zeros((self.num_samples, len(nodes)), device=self.device, dtype=torch.float64)

        if not isinstance(self.noise_distributions, dict):
            raise ValueError("noise_distributions must be a dictionary.")
        if not all(node in self.noise_distributions for node in self.graph.getNodes()):
            raise ValueError("noise_distributions must contain an entry for each node in the graph.")
        if not all(isinstance(self.noise_distributions[node], NoiseDistribution) for node in self.graph.getNodes()):
            raise ValueError("All values in noise_distributions must be instances of the NoiseDistribution class.")

        for node in valid_order:
            parents = list(self.graph.getParents(node))
            mlp = self.node_to_mlp[node]

            # Prepare inputs for the MLP
            parent_indices = [node_to_index[parent] for parent in parents]
            parent_data = data[:, parent_indices]  # Shape: (num_samples, len(parents))
            sample = self.noise_distributions[node].sample(self.num_samples)
            noise = torch.tensor(sample, dtype=torch.float64, device=self.device).unsqueeze(1)

            # Combine parent data and noise
            inputs = torch.cat((parent_data, noise), dim=1)

            # Pass inputs through the MLP
            node_data = mlp(inputs).squeeze()

            # Rescale the data if necessary
            if self.rescale_min is not None and self.rescale_max is not None \
                    and self.variable_types[node] == "continuous":
                node_data = self.rescale_data(node_data)

            # Store the generated data for this node
            data[:, node_to_index[node]] = node_data

        # numpy_data = data.cpu().detach().numpy()
        numpy_data = data.cpu().detach().numpy().astype(np.float64)

        # Convert the numpy array to a Pandas DataFrame
        column_names = list(self.graph.getNodes())
        df = pd.DataFrame(numpy_data, columns=column_names)

        # Set dtypes for each column based on variable type
        for node in self.graph.getNodes():
            if self.variable_types[node] == "continuous":
                df[node] = df[node].astype(np.float64)
            else:
                df[node] = df[node].astype(np.int32)

        return df

    def rescale_data(self, column, epsilon=1e-8):
        """
        Rescale a data column to the specified range [rescale_min, rescale_max].
        """
        col_min, col_max = column.min(), column.max()
        if col_max - col_min > epsilon:
            return self.rescale_min + (column - col_min) * (self.rescale_max - self.rescale_min) / (col_max - col_min)
        return column

    @staticmethod
    def initialize_weights(mlp, nonlinearity='relu'):
        """
        Initialize the weights of an MLP using Kaiming initialization for weights
        and normal initialization for biases.
        """
        for layer in mlp.layers:
            if isinstance(layer, nn.Linear):
                nn.init.kaiming_uniform_(layer.weight, nonlinearity=nonlinearity)
                # nn.init.normal_(layer.bias, mean=0.0, std=0.01)

    @staticmethod
    def is_acyclic(graph):
        return not graph.paths().existsDirectedCycle()

    @staticmethod
    def topological_sort(graph):
        return graph.paths().getValidOrder(graph.getNodes(), True)
