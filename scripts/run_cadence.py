"""
Cadence prediction benchmark.

Evaluates whether the model assigns lowest NLL to the tonic resolution (I) when
given I–IV–I–V progressions in all 12 keys. Data: cadence/*.mid under benchmark_suite.
"""
import numpy as np
import pandas as pd


def run_cadence_prediction_benchmark(
    get_mean_nll,
    path_to_benchmark_suite,
    return_all_results=False,
):
    """
    Run the cadence prediction benchmark.

    For each of 12 tonic keys (MIDI 60–71), the benchmark loads cadence stimuli
    resolving to each of 12 keys (major, minor, diminished). The model’s mean NLL
    is computed per file; the tonic resolution (key 0) is ranked among the 12 options.
    The score is the average percentile of the tonic (higher = better).

    Parameters
    ----------
    get_mean_nll : callable (str -> float)
        Function that takes a path to a MIDI file and returns the mean
        negative log-likelihood over the sequence.
    path_to_benchmark_suite : str
        Path to the benchmark_suite directory (must contain a "cadence/" subdir
        with files like ``{60+i}_from_I-IV-I-V_to_{j}_maj.min.mid``).
    return_all_results : bool, optional
        If True, return (dataframe of tonic percentile per key, mean_percentile).
        If False, return only mean_percentile. Default is False.

    Returns
    -------
    float or tuple
        If return_all_results is False: mean percentile of tonic across keys (float).
        If True: (all_results DataFrame, mean_percentile float).
    """
    all_maj = []
    all_min = []
    all_dim = []

    for i in range(12):
        maj_nll = []
        min_nll = []
        dim_nll = []

        for j in range(12):
            major = (
                path_to_benchmark_suite
                + "cadence/"
                + str(60 + i)
                + "_from_I-IV-I-V_to_"
                + str(j)
                + "_maj.mid"
            )
            minor = (
                path_to_benchmark_suite
                + "cadence/"
                + str(60 + i)
                + "_from_I-IV-I-V_to_"
                + str(j)
                + "_min.mid"
            )
            dimin = (
                path_to_benchmark_suite
                + "cadence/"
                + str(60 + i)
                + "_from_I-IV-I-V_to_"
                + str(j)
                + "_dim.mid"
            )

            maj_nll.append(get_mean_nll(major))
            min_nll.append(get_mean_nll(minor))
            dim_nll.append(get_mean_nll(dimin))

        all_maj.append(maj_nll)
        all_min.append(min_nll)
        all_dim.append(dim_nll)

    all_maj = pd.DataFrame(all_maj, columns=[str(x) + "_maj" for x in range(0, 12)]).T
    all_min = pd.DataFrame(all_min, columns=[str(x) + "_min" for x in range(0, 12)]).T
    all_dim = pd.DataFrame(all_dim, columns=[str(x) + "_dim" for x in range(0, 12)]).T

    all_results = pd.concat([all_maj, all_min, all_dim])
    all_results = (-all_results).rank(0, pct=True).T[["0_maj"]].rename(
        columns={"0_maj": "Percentile of tonic"}
    )
    mean_percentile = np.mean(all_results)

    if return_all_results:
        return all_results, mean_percentile
    return mean_percentile
