import numpy as np
import pandas as pd


def trimmed_mean(x: pd.Series, trim: float = 0.1) -> float:
    """Calculate trimmed mean of a series"""
    return x.sort_values()[int(len(x) * trim) : int(len(x) * (1 - trim))].mean()


def maxentboot(x: pd.Series, num_replicates=9999, trim=0.1):
    """Maximum Entropy Time Series Bootstrap"""
    if not isinstance(x, pd.Series):
        raise TypeError("`x` should be a pandas.Series")

    # 1. Sort and store ordering
    sorted_x = x.sort_values()
    xt = sorted_x.values

    # 2-3. Compute trimmed mean and intermediate points
    trm = trimmed_mean(x.diff().abs())
    zt = np.hstack((xt[0] - trm, (xt[:-1] + xt[1:]) / 2, xt[-1] + trm))

    # 4. Compute means for intervals
    desired_means = np.hstack(
        (
            0.75 * xt[0] + 0.25 * xt[1],
            0.25 * xt[:-2] + 0.5 * xt[1:-1] + 0.25 * xt[2:],
            0.75 * xt[-1] + 0.25 * xt[-2],
        )
    )

    # 5. Generate and process random numbers
    xr = np.linspace(0, 1, len(x) + 1)
    U = np.sort(np.random.rand(num_replicates, len(x))).transpose()
    inds = np.searchsorted(xr, U, side="right") - 1

    lin_interp = desired_means[inds] - (zt[inds] + zt[inds + 1]) / 2
    y0 = zt[inds] + lin_interp
    y1 = zt[inds + 1] + lin_interp
    quantiles = y0 + ((U - xr[inds]) * (y1 - y0)) / (xr[inds + 1] - xr[inds])

    # 6. Create and reorder replicates
    replicates = pd.DataFrame(quantiles, index=sorted_x.index)
    return replicates.reindex(x.index)
