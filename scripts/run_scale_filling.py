"""
Scale filling benchmark.

Evaluates whether the model prefers the correct scale-degree completion over
incorrect alternatives across keys. Data: scale_filling/*.mid (correct, incorrect,
and control files per pitch). Uses total NLL with control subtraction for normalization.
"""
import glob
import numpy as np
import pandas as pd


def run_scale_filling_benchmark(
    get_total_nll,
    path_to_benchmark_suite,
    return_all_results=False,
):
    """
    Run the scale filling benchmark.

    For each pitch in 48–72 (MIDI), the benchmark loads one correct scale completion
    and multiple incorrect alternatives, plus control files. Total NLL is computed
    and normalized by subtracting the control NLL. The correct completion is ranked
    among the options; the score is the average percentile of the correct answer
    across keys (higher = better).

    Parameters
    ----------
    get_total_nll : callable (str -> float)
        Function that takes a path to a MIDI file and returns the total
        negative log-likelihood over the sequence.
    path_to_benchmark_suite : str
        Path to the benchmark_suite directory (must contain "scale_filling/"
        with files like ``{pitch}_*correct*.mid`` and ``{pitch}_*_control.mid``).
    return_all_results : bool, optional
        If True, return (dataframe of percentile per key, mean_percentile).
        If False, return only mean_percentile. Default is False.

    Returns
    -------
    float or tuple
        If return_all_results is False: mean percentile (float).
        If True: (all_results DataFrame, mean_percentile float).
    """
    all_correct_nlls = []
    all_incorrect_nlls = []

    for i in range(48, 73):
        all_files = glob.glob(
            path_to_benchmark_suite + "scale_filling/" + str(i) + "_*"
        )
        correct = [
            x
            for x in all_files
            if (x.endswith("mid")) and ("correct" in x) and ("control" not in x)
        ][0]
        correct_control = correct.split(".mid")[0] + "_control.mid"

        wrong = [
            x
            for x in all_files
            if (x.endswith("mid")) and ("correct" not in x) and ("control" not in x)
        ]
        wrong_control = [x.split(".mid")[0] + "_control.mid" for x in wrong]

        nll_correct = get_total_nll(correct) - get_total_nll(correct_control)
        nlls_incorrect = [
            get_total_nll(wrong[k]) - get_total_nll(wrong_control[k])
            for k in range(len(wrong))
        ]

        all_correct_nlls.append(nll_correct)
        all_incorrect_nlls.append(nlls_incorrect)

    correct_scale_rank = [
        np.argsort(np.argsort(all_incorrect_nlls[i] + [all_correct_nlls[i]]))[-1] + 1
        for i in range(-12, 13)
    ]
    correct_scale_rank = pd.DataFrame(correct_scale_rank, columns=["Correct Scale Rank"])

    all_results = pd.DataFrame(
        (((24 - correct_scale_rank) + 1) / 24).values, columns=["Average Percentile"]
    )
    mean_percentile = np.mean(all_results)

    if return_all_results:
        return all_results, mean_percentile
    return mean_percentile
