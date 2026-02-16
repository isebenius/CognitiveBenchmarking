"""
Interval recognition benchmark.

Evaluates whether the model assigns lowest NLL to the correct interval when
distinguishing among 25 interval types (-octave to octave). Uses multiple
permutations of stimuli; data: benchmark_suite/interval/perm1/ ... perm5/.
"""
import glob
from collections import defaultdict

import numpy as np
import pandas as pd

INTERVALS = [
    "-octave", "-maj7", "-min7", "-maj6", "-min6", "-p5", "-tritone", "-p4",
    "-maj3", "-min3", "-maj2", "-min2", "unison",
    "min2", "maj2", "min3", "maj3", "p4", "tritone", "p5",
    "min6", "maj6", "min7", "maj7", "octave",
]


def run_interval_recognition_benchmark(
    get_mean_nll,
    path_to_benchmark_suite,
    return_all_results=False,
    n_perm=5,
):
    """
    Run the interval recognition benchmark.

    For each interval type (e.g. perfect fifth, minor third), the benchmark loads
    correct and foil MIDIs from n_perm permutation folders. The model’s mean NLL
    is computed per file; the correct interval is ranked among the 25 options per
    permutation. The score is the average percentile of the correct interval
    across intervals and permutations (higher = better).

    Parameters
    ----------
    get_mean_nll : callable (str -> float)
        Function that takes a path to a MIDI file and returns the mean NLL.
    path_to_benchmark_suite : str
        Path to the benchmark_suite directory (must contain "interval/perm1/",
        "interval/perm2/", ... with files per interval).
    return_all_results : bool, optional
        If True, return (dataframe of percentile per interval and permutation,
        mean_percentile). If False, return only mean_percentile. Default is False.
    n_perm : int, optional
        Number of permutation folders to use (e.g. 5 for perm1..perm5). Default is 5.

    Returns
    -------
    float or tuple
        If return_all_results is False: mean percentile (float).
        If True: (final_results_df DataFrame, mean_percentile float).
    """
    final_results = defaultdict(list)

    for interval in INTERVALS:
        results = {key: [] for key in INTERVALS}

        for i in range(1, n_perm + 1):
            tests = glob.glob(
                path_to_benchmark_suite + "interval/perm" + str(i) + "/" + interval + "*"
            )
            test_intervals = [x.split(".mid")[0].split("_")[-1] for x in tests]
            tests_dict = dict(zip(test_intervals, tests))

            keys = []
            nlls = []

            for key, value in tests_dict.items():
                keys.append(key)
                nlls.append(get_mean_nll(value))

            min_nll = np.min(nlls)
            nlls = np.array(nlls) - min_nll

            for j, x in enumerate(keys):
                if x == "correct":
                    results[interval].append(nlls[j])
                else:
                    results[x].append(nlls[j])

        target_relative_nlls = pd.DataFrame(results).T.rank(axis=0).T[interval]
        final_results[interval] = list(target_relative_nlls.values.flatten())

    final_results_df = pd.DataFrame(
        final_results, index=["Permutation " + str(x) for x in range(1, n_perm + 1)]
    )
    final_results_df = ((24 - final_results_df) + 1) / 24

    mean_percentile = final_results_df.mean().mean()

    if return_all_results:
        return final_results_df, mean_percentile
    return mean_percentile
