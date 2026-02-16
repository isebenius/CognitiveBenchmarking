"""
Human melody continuation alignment benchmark.

Compares model NLL for melody continuations (Lokyan t_01 stimuli) with human
ratings. Continuations are from C4 and F#4 contexts; correlation is computed
per context interval and averaged. Data: benchmark_suite/melody_continuation/.
"""
import glob
import numpy as np
import pandas as pd
from scipy import stats

CONTEXT_INTERVALS = ["M2_a", "M2_d", "M6_a", "M6_d", "m3_a", "m3_d", "m7_a", "m7_d"]
ENDING_NOTES = ["C4", "F#4"]


def human_melody_comparison(
    get_mean_nll,
    path_to_benchmark_suite,
    human_ranking_data_loc=None,
    return_all_results=False,
):
    """
    Run the human melody continuation alignment benchmark.

    For each context interval (e.g. M2_a, m7_d) and each ending key (C4, F#4),
    the model’s mean NLL is computed for 25 continuation MIDIs. These are
    correlated (Spearman) with human ratings (lower NLL should align with higher
    rating). The score is the average of these correlations across context
    intervals, using normalized NLL across the two keys.

    Parameters
    ----------
    get_mean_nll : callable (str -> float)
        Function that takes a path to a MIDI file and returns the mean NLL.
    path_to_benchmark_suite : str
        Path to the benchmark_suite directory (must contain "melody_continuation/"
        with continuation MIDIs and optionally Lokyan_t_01_human_processed_ratings.csv).
    human_ranking_data_loc : str, optional
        Path to the human ratings CSV (Lokyan t_01). If None, defaults to
        path_to_benchmark_suite + "melody_continuation/Lokyan_t_01_human_processed_ratings.csv".
    return_all_results : bool, optional
        If True, return (dataframe of correlations per context and key,
        mean_correlation). If False, return only mean_correlation. Default is False.

    Returns
    -------
    float or tuple
        If return_all_results is False: mean correlation (float).
        If True: (model_human_corrs DataFrame, mean_correlation float).
    """
    if human_ranking_data_loc is None:
        human_ranking_data_loc = (
            path_to_benchmark_suite + "melody_continuation/Lokyan_t_01_human_processed_ratings.csv"
        )

    c_results = pd.DataFrame(index=range(1, 26), columns=CONTEXT_INTERVALS)

    for interval in CONTEXT_INTERVALS:
        results = {key: [] for key in range(1, 26)}
        for i in range(1, 26):
            fname = glob.glob(
                path_to_benchmark_suite
                + "melody_continuation/"
                + interval
                + "_from_C4_cont_"
                + str(i)
                + "_*.mid"
            )[0]
            results[i].append(get_mean_nll(fname))
        results = pd.DataFrame(results, index=[interval]).T
        c_results[interval] = results[interval]

    f_sharp_results = pd.DataFrame(index=range(1, 26), columns=CONTEXT_INTERVALS)
    for interval in CONTEXT_INTERVALS:
        results = {key: [] for key in range(1, 26)}
        for i in range(1, 26):
            fname = glob.glob(
                path_to_benchmark_suite
                + "melody_continuation/"
                + interval
                + "_from_F#4_cont_"
                + str(i)
                + "_*.mid"
            )[0]
            results[i].append(get_mean_nll(fname))
        results = pd.DataFrame(results, index=[interval]).T
        f_sharp_results[interval] = results[interval]

    human_results = pd.read_csv(human_ranking_data_loc, index_col=0)
    human_results_reformatted = pd.DataFrame(
        index=range(1, 26), columns=CONTEXT_INTERVALS
    )
    for x, dat in human_results.groupby("stim_identity"):
        human_results_reformatted[x] = dat["mean_rating"].values

    model_human_corrs = pd.DataFrame(
        index=CONTEXT_INTERVALS, columns=ENDING_NOTES + ["average"]
    )
    c_results_norm = (c_results - c_results.mean()) / c_results.std()
    f_sharp_results_norm = (
        f_sharp_results - f_sharp_results.mean()
    ) / f_sharp_results.std()

    for interval in CONTEXT_INTERVALS:
        model_human_corrs.at[interval, "C4"] = stats.spearmanr(
            c_results[interval], -human_results_reformatted[interval]
        )[0]
        model_human_corrs.at[interval, "F#4"] = stats.spearmanr(
            f_sharp_results[interval], -human_results_reformatted[interval]
        )[0]
        model_human_corrs.at[interval, "average"] = stats.spearmanr(
            ((c_results_norm + f_sharp_results_norm) / 2)[interval],
            -human_results_reformatted[interval],
        )[0]

    mean_correlation = np.mean(model_human_corrs["average"])

    if return_all_results:
        return model_human_corrs, mean_correlation
    return mean_correlation
