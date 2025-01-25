"""
risk/network/plot/network
~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from typing import Any, Dict, List, Tuple, Union

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from risk.log import params
from risk.network.graph.network import NetworkGraph
from risk.network.plot.canvas import Canvas
from risk.network.plot.contour import Contour
from risk.network.plot.labels import Labels
from risk.network.plot.utils.colors import get_domain_colors, to_rgba
from risk.network.plot.utils.layout import calculate_bounding_box


class Network:
    """A class for plotting network graphs with customizable options.

    The Network class provides methods to plot network graphs with flexible node and edge properties.
    """

    def __init__(self, graph: NetworkGraph, ax: Any = None) -> None:
        """Initialize the NetworkPlotter class.

        Args:
            graph (NetworkGraph): The network data and attributes to be visualized.
            ax (Any, optional): Axes object to plot the network graph. Defaults to None.
        """
        self.graph = graph
        self.ax = ax

    def plot_network(
        self,
        node_size: Union[int, np.ndarray] = 50,
        node_shape: str = "o",
        node_edgewidth: float = 1.0,
        edge_width: float = 1.0,
        node_color: Union[str, List, Tuple, np.ndarray] = "white",
        node_edgecolor: Union[str, List, Tuple, np.ndarray] = "black",
        edge_color: Union[str, List, Tuple, np.ndarray] = "black",
        node_alpha: Union[float, None] = 1.0,
        edge_alpha: Union[float, None] = 1.0,
    ) -> None:
        """Plot the network graph with customizable node colors, sizes, edge widths, and node edge widths.

        Args:
            node_size (int or np.ndarray, optional): Size of the nodes. Can be a single integer or an array of sizes. Defaults to 50.
            node_shape (str, optional): Shape of the nodes. Defaults to "o".
            node_edgewidth (float, optional): Width of the node edges. Defaults to 1.0.
            edge_width (float, optional): Width of the edges. Defaults to 1.0.
            node_color (str, List, Tuple, or np.ndarray, optional): Color of the nodes. Can be a single color or an array of colors.
                Defaults to "white".
            node_edgecolor (str, List, Tuple, or np.ndarray, optional): Color of the node edges. Can be a single color or an array of colors.
                Defaults to "black".
            edge_color (str, List, Tuple, or np.ndarray, optional): Color of the edges. Can be a single color or an array of colors.
                Defaults to "black".
            node_alpha (float, None, optional): Alpha value (transparency) for the nodes. If provided, it overrides any existing alpha
                values found in node_color. Defaults to 1.0. Annotated node_color alphas will override this value.
            edge_alpha (float, None, optional): Alpha value (transparency) for the edges. If provided, it overrides any existing alpha
                values found in edge_color. Defaults to 1.0.
        """
        # Log the plotting parameters
        params.log_plotter(
            network_node_size=(
                "custom" if isinstance(node_size, np.ndarray) else node_size
            ),  # np.ndarray usually indicates custom sizes
            network_node_shape=node_shape,
            network_node_edgewidth=node_edgewidth,
            network_edge_width=edge_width,
            network_node_color=(
                "custom" if isinstance(node_color, np.ndarray) else node_color
            ),  # np.ndarray usually indicates custom colors
            network_node_edgecolor=node_edgecolor,
            network_edge_color=edge_color,
            network_node_alpha=node_alpha,
            network_edge_alpha=edge_alpha,
        )

        # Convert colors to RGBA using the to_rgba helper function
        # If node_colors was generated using get_annotated_node_colors, its alpha values will override node_alpha
        node_color_rgba = to_rgba(
            color=node_color, alpha=node_alpha, num_repeats=len(self.graph.network.nodes)
        )
        node_edgecolor_rgba = to_rgba(
            color=node_edgecolor, alpha=1.0, num_repeats=len(self.graph.network.nodes)
        )
        edge_color_rgba = to_rgba(
            color=edge_color, alpha=edge_alpha, num_repeats=len(self.graph.network.edges)
        )

        # Extract node coordinates from the network graph
        node_coordinates = self.graph.node_coordinates

        # Draw the nodes of the graph
        nx.draw_networkx_nodes(
            self.graph.network,
            pos=node_coordinates,
            node_size=node_size,
            node_shape=node_shape,
            node_color=node_color_rgba,
            edgecolors=node_edgecolor_rgba,
            linewidths=node_edgewidth,
            ax=self.ax,
        )
        # Draw the edges of the graph
        nx.draw_networkx_edges(
            self.graph.network,
            pos=node_coordinates,
            width=edge_width,
            edge_color=edge_color_rgba,
            ax=self.ax,
        )

    def plot_subnetwork(
        self,
        nodes: Union[List, Tuple, np.ndarray],
        node_size: Union[int, np.ndarray] = 50,
        node_shape: str = "o",
        node_edgewidth: float = 1.0,
        edge_width: float = 1.0,
        node_color: Union[str, List, Tuple, np.ndarray] = "white",
        node_edgecolor: Union[str, List, Tuple, np.ndarray] = "black",
        edge_color: Union[str, List, Tuple, np.ndarray] = "black",
        node_alpha: Union[float, None] = None,
        edge_alpha: Union[float, None] = None,
    ) -> None:
        """Plot a subnetwork of selected nodes with customizable node and edge attributes.

        Args:
            nodes (List, Tuple, or np.ndarray): List of node labels to include in the subnetwork. Accepts nested lists.
            node_size (int or np.ndarray, optional): Size of the nodes. Can be a single integer or an array of sizes. Defaults to 50.
            node_shape (str, optional): Shape of the nodes. Defaults to "o".
            node_edgewidth (float, optional): Width of the node edges. Defaults to 1.0.
            edge_width (float, optional): Width of the edges. Defaults to 1.0.
            node_color (str, List, Tuple, or np.ndarray, optional): Color of the nodes. Defaults to "white".
            node_edgecolor (str, List, Tuple, or np.ndarray, optional): Color of the node edges. Defaults to "black".
            edge_color (str, List, Tuple, or np.ndarray, optional): Color of the edges. Defaults to "black".
            node_alpha (float, None, optional): Transparency for the nodes. If provided, it overrides any existing alpha values
                found in node_color. Defaults to 1.0.
            edge_alpha (float, None, optional): Transparency for the edges. If provided, it overrides any existing alpha values
                found in node_color. Defaults to 1.0.

        Raises:
            ValueError: If no valid nodes are found in the network graph.
        """
        # Flatten nested lists of nodes, if necessary
        if any(isinstance(item, (list, tuple, np.ndarray)) for item in nodes):
            nodes = [node for sublist in nodes for node in sublist]

        # Filter to get node IDs and their coordinates
        node_ids = [
            self.graph.node_label_to_node_id_map.get(node)
            for node in nodes
            if node in self.graph.node_label_to_node_id_map
        ]
        if not node_ids:
            raise ValueError("No nodes found in the network graph.")

        # Check if node_color is a single color or a list of colors
        if not isinstance(node_color, (str, Tuple, np.ndarray)):
            node_color = [
                node_color[nodes.index(node)]
                for node in nodes
                if node in self.graph.node_label_to_node_id_map
            ]

        # Convert colors to RGBA using the to_rgba helper function
        node_color_rgba = to_rgba(color=node_color, alpha=node_alpha, num_repeats=len(node_ids))
        node_edgecolor_rgba = to_rgba(color=node_edgecolor, alpha=1.0, num_repeats=len(node_ids))
        edge_color_rgba = to_rgba(
            color=edge_color, alpha=edge_alpha, num_repeats=len(self.graph.network.edges)
        )

        # Get the coordinates of the filtered nodes
        node_coordinates = {node_id: self.graph.node_coordinates[node_id] for node_id in node_ids}

        # Draw the nodes in the subnetwork
        nx.draw_networkx_nodes(
            self.graph.network,
            pos=node_coordinates,
            nodelist=node_ids,
            node_size=node_size,
            node_shape=node_shape,
            node_color=node_color_rgba,
            edgecolors=node_edgecolor_rgba,
            linewidths=node_edgewidth,
            ax=self.ax,
        )
        # Draw the edges between the specified nodes in the subnetwork
        subgraph = self.graph.network.subgraph(node_ids)
        nx.draw_networkx_edges(
            subgraph,
            pos=node_coordinates,
            width=edge_width,
            edge_color=edge_color_rgba,
            ax=self.ax,
        )

    def get_annotated_node_colors(
        self,
        cmap: str = "gist_rainbow",
        color: Union[str, List, Tuple, np.ndarray, None] = None,
        blend_colors: bool = False,
        blend_gamma: float = 2.2,
        min_scale: float = 0.8,
        max_scale: float = 1.0,
        scale_factor: float = 1.0,
        alpha: Union[float, None] = 1.0,
        nonsignificant_color: Union[str, List, Tuple, np.ndarray] = "white",
        nonsignificant_alpha: Union[float, None] = 1.0,
        ids_to_colors: Union[Dict[int, Any], None] = None,
        random_seed: int = 888,
    ) -> np.ndarray:
        """Adjust the colors of nodes in the network graph based on significance.

        Args:
            cmap (str, optional): Colormap to use for coloring the nodes. Defaults to "gist_rainbow".
            color (str, List, Tuple, np.ndarray, or None, optional): Color to use for the nodes. Can be a single color or an array of colors.
                If None, the colormap will be used. Defaults to None.
            blend_colors (bool, optional): Whether to blend colors for nodes with multiple domains. Defaults to False.
            blend_gamma (float, optional): Gamma correction factor for perceptual color blending. Defaults to 2.2.
            min_scale (float, optional): Minimum scale for color intensity. Defaults to 0.8.
            max_scale (float, optional): Maximum scale for color intensity. Defaults to 1.0.
            scale_factor (float, optional): Factor for adjusting the color scaling intensity. Defaults to 1.0.
            alpha (float, None, optional): Alpha value for significant nodes. If provided, it overrides any existing alpha values found in `color`.
                Defaults to 1.0.
            nonsignificant_color (str, List, Tuple, or np.ndarray, optional): Color for non-significant nodes. Can be a single color or an array of colors.
                Defaults to "white".
            nonsignificant_alpha (float, None, optional): Alpha value for non-significant nodes. If provided, it overrides any existing alpha values found
                in `nonsignificant_color`. Defaults to 1.0.
            ids_to_colors (Dict[int, Any], None, optional): Mapping of domain IDs to specific colors. Defaults to None.
            random_seed (int, optional): Seed for random number generation. Defaults to 888.

        Returns:
            np.ndarray: Array of RGBA colors adjusted for significance status.
        """
        # Get the initial domain colors for each node, which are returned as RGBA
        network_colors = get_domain_colors(
            graph=self.graph,
            cmap=cmap,
            color=color,
            blend_colors=blend_colors,
            blend_gamma=blend_gamma,
            min_scale=min_scale,
            max_scale=max_scale,
            scale_factor=scale_factor,
            ids_to_colors=ids_to_colors,
            random_seed=random_seed,
        )
        # Apply the alpha value for significant nodes
        network_colors[:, 3] = alpha  # Apply the alpha value to the significant nodes' A channel
        # Convert the non-significant color to RGBA using the to_rgba helper function
        nonsignificant_color_rgba = to_rgba(
            color=nonsignificant_color, alpha=nonsignificant_alpha, num_repeats=1
        )  # num_repeats=1 for a single color
        # Adjust node colors: replace any nodes where all three RGB values are equal and less than or equal to 0.1
        # 0.1 is a predefined threshold for the minimum color intensity
        adjusted_network_colors = np.where(
            (
                np.all(network_colors[:, :3] <= 0.1, axis=1)
                & np.all(network_colors[:, :3] == network_colors[:, 0:1], axis=1)
            )[:, None],
            np.tile(
                np.array(nonsignificant_color_rgba), (network_colors.shape[0], 1)
            ),  # Replace with the full RGBA non-significant color
            network_colors,  # Keep the original colors where no match is found
        )
        return adjusted_network_colors

    def get_annotated_node_sizes(
        self, significant_size: int = 50, nonsignificant_size: int = 25
    ) -> np.ndarray:
        """Adjust the sizes of nodes in the network graph based on whether they are significant or not.

        Args:
            significant_size (int): Size for significant nodes. Defaults to 50.
            nonsignificant_size (int): Size for non-significant nodes. Defaults to 25.

        Returns:
            np.ndarray: Array of node sizes, with significant nodes larger than non-significant ones.
        """
        # Merge all significant nodes from the domain_id_to_node_ids_map dictionary
        significant_nodes = set()
        for _, node_ids in self.graph.domain_id_to_node_ids_map.items():
            significant_nodes.update(node_ids)

        # Initialize all node sizes to the non-significant size
        node_sizes = np.full(len(self.graph.network.nodes), nonsignificant_size)
        # Set the size for significant nodes
        for node in significant_nodes:
            if node in self.graph.network.nodes:
                node_sizes[node] = significant_size

        return node_sizes


class NetworkPlotter(Canvas, Network, Contour, Labels):
    """A class for visualizing network graphs with customizable options.

    The NetworkPlotter class uses a NetworkGraph object and provides methods to plot the network with
    flexible node and edge properties. It also supports plotting labels, contours, drawing the network's
    perimeter, and adjusting background colors.
    """

    def __init__(
        self,
        graph: NetworkGraph,
        figsize: Tuple = (10, 10),
        background_color: Union[str, List, Tuple, np.ndarray] = "white",
        background_alpha: Union[float, None] = 1.0,
        pad: float = 0.3,
    ) -> None:
        """Initialize the NetworkPlotter with a NetworkGraph object and plotting parameters.

        Args:
            graph (NetworkGraph): The network data and attributes to be visualized.
            figsize (Tuple, optional): Size of the figure in inches (width, height). Defaults to (10, 10).
            background_color (str, List, Tuple, np.ndarray, optional): Background color of the plot. Defaults to "white".
            background_alpha (float, None, optional): Transparency level of the background color. If provided, it overrides
                any existing alpha values found in background_color. Defaults to 1.0.
            pad (float, optional): Padding value to adjust the axis limits. Defaults to 0.3.
        """
        self.graph = graph
        # Initialize the plot with the specified parameters
        self.ax = self._initialize_plot(
            graph=graph,
            figsize=figsize,
            background_color=background_color,
            background_alpha=background_alpha,
            pad=pad,
        )
        super().__init__(graph=graph, ax=self.ax)

    def _initialize_plot(
        self,
        graph: NetworkGraph,
        figsize: Tuple,
        background_color: Union[str, List, Tuple, np.ndarray],
        background_alpha: Union[float, None],
        pad: float,
    ) -> plt.Axes:
        """Set up the plot with figure size and background color.

        Args:
            graph (NetworkGraph): The network data and attributes to be visualized.
            figsize (Tuple): Size of the figure in inches (width, height).
            background_color (str, List, Tuple, or np.ndarray): Background color of the plot. Can be a single color or an array of colors.
            background_alpha (float, None, optional): Transparency level of the background color. If provided, it overrides any existing
                alpha values found in `background_color`.
            pad (float, optional): Padding value to adjust the axis limits.

        Returns:
            plt.Axes: The axis object for the plot.
        """
        # Log the plotter settings
        params.log_plotter(
            figsize=figsize,
            background_color=background_color,
            background_alpha=background_alpha,
            pad=pad,
        )

        # Extract node coordinates from the network graph
        node_coordinates = graph.node_coordinates
        # Calculate the center and radius of the bounding box around the network
        center, radius = calculate_bounding_box(node_coordinates)

        # Create a new figure and axis for plotting
        fig, ax = plt.subplots(figsize=figsize)
        fig.tight_layout()  # Adjust subplot parameters to give specified padding
        # Set axis limits based on the calculated bounding box and radius
        ax.set_xlim([center[0] - radius - pad, center[0] + radius + pad])
        ax.set_ylim([center[1] - radius - pad, center[1] + radius + pad])
        ax.set_aspect("equal")  # Ensure the aspect ratio is equal

        # Set the background color of the plot
        # Convert color to RGBA using the to_rgba helper function
        fig.patch.set_facecolor(
            to_rgba(color=background_color, alpha=background_alpha, num_repeats=1)
        )  # num_repeats=1 for single color
        ax.invert_yaxis()  # Invert the y-axis to match typical image coordinates
        # Remove axis spines for a cleaner look
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Hide axis ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.patch.set_visible(False)  # Hide the axis background

        return ax

    @staticmethod
    def savefig(*args, pad_inches: float = 0.5, dpi: int = 100, **kwargs) -> None:
        """Save the current plot to a file with additional export options.

        Args:
            *args: Positional arguments passed to `plt.savefig`.
            pad_inches (float, optional): Padding around the figure when saving. Defaults to 0.5.
            dpi (int, optional): Dots per inch (DPI) for the exported image. Defaults to 300.
            **kwargs: Keyword arguments passed to `plt.savefig`, such as filename and format.
        """
        # Ensure user-provided kwargs take precedence
        kwargs.setdefault("dpi", dpi)
        kwargs.setdefault("pad_inches", pad_inches)
        # Ensure the plot is saved with tight bounding box if not specified
        kwargs.setdefault("bbox_inches", "tight")
        # Call plt.savefig with combined arguments
        plt.savefig(*args, **kwargs)

    @staticmethod
    def show(*args, **kwargs) -> None:
        """Display the current plot.

        Args:
            *args: Positional arguments passed to `plt.show`.
            **kwargs: Keyword arguments passed to `plt.show`.
        """
        plt.show(*args, **kwargs)
