from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_replicates(
    original_data: pd.Series,
    replicates: Union[np.ndarray, pd.DataFrame],
    title: str = "Bootstrap Replicates",
    alpha: float = 0.1,
    n_replicates: int = None,
):
    """Plot bootstrap replicates with original series."""
    plt.figure(figsize=(12, 6))

    # Handle DataFrame replicates
    if isinstance(replicates, pd.DataFrame):
        replicates = replicates.iloc[:, :n_replicates] if n_replicates else replicates
        plt.plot(
            original_data.index,
            replicates.values,
            color="blue",
            alpha=alpha,
            label="Replicates",
        )
        plt.plot(
            original_data.index,
            original_data,
            color="red",
            linewidth=2,
            label="Original",
        )
    else:
        # Handle numpy array replicates
        x = np.arange(len(original_data))
        plot_data = replicates[:, :n_replicates] if n_replicates else replicates
        plt.plot(x, plot_data, color="blue", alpha=alpha, label="Replicates")
        plt.plot(x, original_data, color="red", linewidth=2, label="Original")

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
