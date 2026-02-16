"""
Cognitive benchmarking suite: run functions for all eight benchmarks.

Import from this module to use the benchmark runners in your own code or
notebooks, e.g.:

    from benchmarks import (
        run_cadence_prediction_benchmark,
        run_scale_filling_benchmark,
        human_melody_comparison,
        ...
    )

Each function is also runnable from the command line via the scripts in
scripts/ (e.g. python -m scripts.run_cadence).
"""

from scripts.run_cadence import run_cadence_prediction_benchmark
from scripts.run_chord_alignment import human_chord_comparison
from scripts.run_glass import run_glass_benchmark
from scripts.run_interval_recognition import run_interval_recognition_benchmark
from scripts.run_melody_continuation import human_melody_comparison
from scripts.run_mussorgsky import run_mussorgsky_benchmark
from scripts.run_scale_filling import run_scale_filling_benchmark
from scripts.run_transposition_invariance import get_transposition_invariance

__all__ = [
    "run_cadence_prediction_benchmark",
    "run_scale_filling_benchmark",
    "run_interval_recognition_benchmark",
    "get_transposition_invariance",
    "human_melody_comparison",
    "human_chord_comparison",
    "run_glass_benchmark",
    "run_mussorgsky_benchmark",
]
