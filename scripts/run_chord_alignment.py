"""
Human chord alignment benchmark.

Compares model mean NLL for chord stimuli (Lokyan t_03) with human harmony
ratings. Data: benchmark_suite/chord_alignment/ (MIDIs and human ratings CSV).
"""
import pandas as pd
from scipy import stats


def human_chord_comparison(
    get_mean_nll,
    path_to_benchmark_suite,
    human_ranking_data_loc=None,
    return_all_results=False,
):
    """
    Run the human chord alignment benchmark.

    For each chord in the Lokyan t_03 set, the model’s mean NLL is computed on
    the corresponding MIDI file. These NLLs are correlated (Pearson) with human
    mean ratings. Higher correlation indicates better alignment with human
    harmony judgments. No time-dilation marginalization is applied in this
    version; performance may improve if averaging over multiple dilation factors.

    Parameters
    ----------
    get_mean_nll : callable (str -> float)
        Function that takes a path to a MIDI file and returns the mean NLL.
    path_to_benchmark_suite : str
        Path to the benchmark_suite directory (must contain "chord_alignment/"
        with one .mid per chord and optionally Lokyan_t_03_human_processed_ratings.csv).
    human_ranking_data_loc : str, optional
        Path to the human ratings CSV (Lokyan t_03). If None, defaults to
        path_to_benchmark_suite + "chord_alignment/Lokyan_t_03_human_processed_ratings.csv".
    return_all_results : bool, optional
        If True, return (dataframe with model NLL and human ratings per chord,
        correlation). If False, return only correlation. Default is False.

    Returns
    -------
    float or tuple
        If return_all_results is False: Pearson correlation (float).
        If True: (results_all DataFrame, correlation float).
    """
    if human_ranking_data_loc is None:
        human_ranking_data_loc = (
            path_to_benchmark_suite + "chord_alignment/Lokyan_t_03_human_processed_ratings.csv"
        )

    human_results_t03 = pd.read_csv(human_ranking_data_loc, index_col=0)
    chord_rating_path = path_to_benchmark_suite + "chord_alignment/"

    results_human = pd.DataFrame(
        human_results_t03[["mean_ratings"]].values.flatten(),
        index=human_results_t03["full_chord_names"].values.flatten(),
        columns=["mean_ratings"],
    )
    results_model = pd.DataFrame(
        index=human_results_t03["full_chord_names"].values.flatten(),
        columns=["model_mean_NLL"],
    )

    for x in human_results_t03["full_chord_names"].values:
        fname = chord_rating_path + x + ".mid"
        nll = get_mean_nll(fname)
        results_model.at[x, "model_mean_NLL"] = nll

    results_all = results_model.copy()
    results_all["human_ratings"] = results_human["mean_ratings"]

    correlation = stats.pearsonr(
        results_all["human_ratings"].values.flatten().astype(float),
        results_all["model_mean_NLL"].values.flatten().astype(float),
    )[0]

    if return_all_results:
        return results_all, correlation
    return correlation
