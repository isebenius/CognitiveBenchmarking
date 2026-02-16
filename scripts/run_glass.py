"""
Glass surprise benchmark.

Compares model surprisal over time (e.g. from glass.mid) with human surprise
ratings at specific events. Data: benchmark_suite/glass/GlassEvents.txt and
precomputed times/surprisals (e.g. from a CSV).
"""
import numpy as np
import pandas as pd
from scipy import stats


def run_glass_benchmark(
    times,
    surprisals,
    path_to_benchmark_suite,
    human_ratings_loc=None,
    return_all_results=False,
):
    """
    Run the Glass (The Hours) surprise benchmark.

    Human ratings are provided at specific onset times (GlassEvents.txt). The
    model’s surprisal at each of these times is found by nearest-neighbor
    lookup in the (times, surprisals) arrays. The score is the Spearman
    correlation between human rank and model surprisal (higher = better
    alignment). Finer-grained time samples in `times` improve alignment.

    Parameters
    ----------
    times : array-like
        Timestamps in seconds where model surprisal is defined (e.g. from
        NLL-over-time output). More samples give better alignment to event onsets.
    surprisals : array-like
        Model surprisal (or NLL) at each time in `times`; same length as times.
    path_to_benchmark_suite : str
        Path to the benchmark_suite directory (must contain "glass/" with
        GlassEvents.txt, and optionally glass.mid for generating times/surprisals).
    human_ratings_loc : str, optional
        Path to GlassEvents.txt. If None, defaults to
        path_to_benchmark_suite + "glass/GlassEvents.txt".
    return_all_results : bool, optional
        If True, return (dataframe of events with model surprisal added,
        correlation). If False, return only correlation. Default is False.

    Returns
    -------
    float or tuple
        If return_all_results is False: Spearman correlation (float).
        If True: (surprise_events DataFrame with "Model surprisal" column, correlation float).
    """
    if human_ratings_loc is None:
        human_ratings_loc = path_to_benchmark_suite + "glass/GlassEvents.txt"

    surprise_events = pd.read_csv(human_ratings_loc)
    surprise_events["Group"] = ["HS"] * 17 + ["LS"] * 17 + ["US"] * 17
    surprise_events = surprise_events.fillna(0)

    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx, array[idx]

    model_surprisal = [
        surprisals[find_nearest(times, onset)[0]]
        for onset in surprise_events["Onset"].values.flatten()
    ]
    surprise_events["Model surprisal"] = model_surprisal

    correlation = stats.spearmanr(surprise_events["Rank"], model_surprisal)[0]

    if return_all_results:
        return surprise_events, correlation
    return correlation
