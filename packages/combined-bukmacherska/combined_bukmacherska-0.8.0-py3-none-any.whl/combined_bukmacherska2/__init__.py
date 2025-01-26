"""
__init__.py for the combined_bukmacherska2 project.

This package provides tools for advanced machine learning model training,
statistical analysis, and data visualization tailored for sports and betting analytics.

Modules:
- `train_models`: Comprehensive utilities for training a wide range of classifiers.
- `predict_with_models`: Perform predictions using trained models.
- `plot_results`: Visualize results with 2D and 3D plots.
- `gamma_function`: Includes mathematical and statistical functions like Gamma and Beta functions.
- `analiza_statystyczna`: Analyze and compute team statistics in a sports context.
"""

from .train_models import train_models, predict_with_models
from .visualizations import plot_results
from .math_utils import gamma_function, beta_function, poisson_probability
from .statistics import oblicz_statystyki_druzyny, analiza_statystyczna
