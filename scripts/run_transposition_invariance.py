"""
Transposition invariance benchmark.

Evaluates whether the model’s interval likelihood profile is stable across
pitch height: correlation of mean NLL vectors for adjacent starting notes
(two octaves above and below middle C). Data: benchmark_suite/transposition/*.mid.
"""
import numpy as np
import pandas as pd

INTERVALS = [
    "neg_octave", "neg_maj7", "neg_min7", "neg_maj6", "neg_min6", "neg_p5",
    "neg_tritone", "neg_p4", "neg_maj3", "neg_min3", "neg_maj2", "neg_min2",
    "unison",
    "min2", "maj2", "min3", "maj3", "p4", "tritone", "p5",
    "min6", "maj6", "min7", "maj7", "octave",
]


def get_transposition_invariance(
    get_mean_nll,
    path_to_benchmark_suite,
    return_all_results=False,
):
    """
    Run the transposition invariance benchmark.

    For each starting note from MIDI 36 to 84 (two octaves below to two above
    middle C), the model’s mean NLL is computed for each of 25 interval stimuli.
    The score is the mean correlation between the NLL vectors of adjacent
    starting notes (higher = more transposition-invariant).

    Parameters
    ----------
    get_mean_nll : callable (str -> float)
        Function that takes a path to a MIDI file and returns the mean NLL.
    path_to_benchmark_suite : str
        Path to the benchmark_suite directory (must contain "transposition/"
        with files like ``pitch{note}_{interval}.mid``).
    return_all_results : bool, optional
        If True, return (dataframe of NLL per note and interval, array of
        adjacent-note correlations). If False, return only mean correlation.
        Default is False.

    Returns
    -------
    float or tuple
        If return_all_results is False: mean correlation (float).
        If True: (all_results DataFrame, invariance array).
    """
    notes = list(range(60 - 24, 60 + 25))
    results = {key: [] for key in notes}

    for note in notes:
        for interval in INTERVALS:
            fname = (
                path_to_benchmark_suite
                + "transposition/"
                + "pitch"
                + str(note)
                + "_"
                + interval
                + ".mid"
            )
            results[note].append(get_mean_nll(fname))

    all_results = pd.DataFrame(results)

    ix_adjacent_notes = np.vstack(
        (np.arange(0, len(notes) - 1), np.arange(1, len(notes)))
    )
    ix_adjacent_notes = tuple(ix_adjacent_notes)

    invariance = all_results.corr().values[ix_adjacent_notes]

    if return_all_results:
        return all_results, invariance
    return np.mean(invariance)
