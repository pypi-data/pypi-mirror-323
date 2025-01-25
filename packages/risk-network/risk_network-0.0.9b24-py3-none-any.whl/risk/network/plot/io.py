"""
risk/network/graph/io
~~~~~~~~~~~~~~~~~~~~~
"""

from typing import List, Tuple, Union

import numpy as np

from risk.log import log_header
from risk.network.graph.network import NetworkGraph
from risk.network.plot.network import NetworkPlotter


class PlotterIO:
    """Handles the loading of network plotter objects.

    The PlotterIO class provides methods to load and configure NetworkPlotter objects for plotting network graphs.
    """

    def __init__() -> None:
        pass

    def load_plotter(
        self,
        graph: NetworkGraph,
        figsize: Union[List, Tuple, np.ndarray] = (10, 10),
        background_color: str = "white",
        background_alpha: Union[float, None] = 1.0,
        pad: float = 0.3,
    ) -> NetworkPlotter:
        """Get a NetworkPlotter object for plotting.

        Args:
            graph (NetworkGraph): The graph to plot.
            figsize (List, Tuple, or np.ndarray, optional): Size of the plot. Defaults to (10, 10)., optional): Size of the figure. Defaults to (10, 10).
            background_color (str, optional): Background color of the plot. Defaults to "white".
            background_alpha (float, None, optional): Transparency level of the background color. If provided, it overrides
                any existing alpha values found in background_color. Defaults to 1.0.
            pad (float, optional): Padding value to adjust the axis limits. Defaults to 0.3.

        Returns:
            NetworkPlotter: A NetworkPlotter object configured with the given parameters.
        """
        log_header("Loading plotter")

        # Initialize and return a NetworkPlotter object
        return NetworkPlotter(
            graph,
            figsize=figsize,
            background_color=background_color,
            background_alpha=background_alpha,
            pad=pad,
        )
