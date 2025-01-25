"""
__init__.py for the combined_bukmacherska project.

This package contains utilities for training machine learning models,
statistical computations, and visualizations for sports and betting analysis.

Modules:
- `train_models`: Functions to train various classifiers.
- `predict_with_models`: Utility to make predictions using trained models.
- `plot_results`: Functions to visualize predictions and statistics.
- `gamma_function`: Functions for mathematical and statistical computations.
- `analiza_statystyczna`: High-level analysis of sports team statistics.
"""

from .train_models import train_models, predict_with_models
from .visualizations import plot_results, rysuj_wykresy
from .math_utils import gamma_function, beta_function, poisson_probability
from .statistics import oblicz_statystyki_druzyny, analiza_statystyczna
