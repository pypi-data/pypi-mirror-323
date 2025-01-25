import numpy as np
from sklearn.linear_model import BayesianRidge
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, 
    AdaBoostClassifier, ExtraTreesClassifier, StackingClassifier, VotingClassifier
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier, Perceptron, PassiveAggressiveClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.experimental import enable_hist_gradient_boosting  # noqa
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.ensemble import BaggingClassifier
from catboost import CatBoostClassifier
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
from scipy.special import gamma, factorial
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Trening modeli
def train_models(X_train, y_train):
    models = {
        'bayesian_ridge': BayesianRidge().fit(X_train, y_train),
        'random_forest': RandomForestClassifier().fit(X_train, y_train),
        'gradient_boosting': GradientBoostingClassifier().fit(X_train, y_train),
        'adaboost': AdaBoostClassifier().fit(X_train, y_train),
        'extra_trees': ExtraTreesClassifier().fit(X_train, y_train),
        'knn': KNeighborsClassifier().fit(X_train, y_train),
        'svm': SVC().fit(X_train, y_train),
        'naive_bayes': GaussianNB().fit(X_train, y_train),
        'decision_tree': DecisionTreeClassifier().fit(X_train, y_train),
        'mlp': MLPClassifier(max_iter=300).fit(X_train, y_train),
        'logistic_regression': LogisticRegression(max_iter=300).fit(X_train, y_train),
        'ridge_classifier': RidgeClassifier().fit(X_train, y_train),
        'lda': LinearDiscriminantAnalysis().fit(X_train, y_train),
        'qda': QuadraticDiscriminantAnalysis().fit(X_train, y_train),
        'catboost': CatBoostClassifier(verbose=0).fit(X_train, y_train),
        'hist_gradient_boosting': HistGradientBoostingClassifier().fit(X_train, y_train),
        'gaussian_process': GaussianProcessClassifier(kernel=RBF()).fit(X_train, y_train),
        'bagging': BaggingClassifier().fit(X_train, y_train),
        'stacking': StackingClassifier(
            estimators=[
                ('lr', LogisticRegression(max_iter=300)),
                ('rf', RandomForestClassifier())
            ]
        ).fit(X_train, y_train),
        'voting': VotingClassifier(
            estimators=[
                ('gb', GradientBoostingClassifier()),
                ('knn', KNeighborsClassifier())
            ],
            voting='soft'
        ).fit(X_train, y_train),
        'perceptron': Perceptron(max_iter=300).fit(X_train, y_train),
        'passive_aggressive': PassiveAggressiveClassifier(max_iter=300).fit(X_train, y_train)
    }

    if XGBClassifier:
        models['xgboost'] = XGBClassifier(use_label_encoder=False, eval_metric='logloss').fit(X_train, y_train)
    else:
        print("XGBoost is not installed. Skipping this model.")

    return models

# Predykcja wyników
def predict_with_models(models, X_test):
    predictions = {model_name: model.predict(X_test) for model_name, model in models.items()}
    return predictions

# Funkcja do rysowania wyników
def plot_results(predictions, team1_lambda, team2_lambda, team1_avg_conceded, team2_avg_conceded):
    fig, axs = plt.subplots(15, 3, figsize=(15, 45))
    events = ['Gole', 'Rzuty rożne', 'Kartki', 'Kontuzje', 'Faule', 'Rzuty karne',
              'Posiadanie piłki', 'Strzały', 'Podania', 'Przejęcia', 'Interwencje']
    for i, event in enumerate(events):
        axs[i * 3].plot([1, 2], [team1_lambda, team2_lambda], marker='o')
        axs[i * 3].set_title(f"{event} - Liniowy")
        axs[i * 3 + 1].bar(['Drużyna 1', 'Drużyna 2'], [team1_lambda, team2_lambda], color=['blue', 'red'])
        axs[i * 3 + 1].set_title(f"{event} - Słupkowy")
        ax1 = fig.add_subplot(15, 3, i * 3 + 2, projection='3d')
        x1 = [0, 1]
        y1 = [team1_lambda, team2_lambda]
        z1 = [team1_avg_conceded, team2_avg_conceded]
        ax1.bar3d(x1, [0] * len(x1), [0] * len(x1), [0.5] * len(x1), y1, z1, color=['blue', 'red'])
        ax1.set_title(f"{event} - 3D")
    plt.tight_layout()
    plt.show()

# Funkcja gamma
def gamma_function(x):
    if int(x) == x and x <= 0:
        raise ValueError("Funkcja gamma nie jest zdefiniowana dla liczb całkowitych ≤ 0.")
    return gamma(x)

# Funkcja beta
def beta_function(x, a, b):
    numerator = gamma(a) * gamma(b)
    denominator = gamma(a + b)
    return numerator / denominator

# Obliczenia Poissona
def poisson_probability(k, lmbda):
    return (lmbda ** k * math.exp(-lmbda)) / factorial(k)

# Funkcja główna do analizy sportowej
def analiza_statystyczna(druzyna1, druzyna2, mecze):
    def oblicz_statystyki_druzyny(gole_zdobyte, gole_stracone, mecze):
        srednia_zdobytych = gole_zdobyte / mecze
        srednia_straconych = gole_stracone / mecze
        return {'zdobyte': srednia_zdobytych, 'stracone': srednia_straconych}

    stat1 = oblicz_statystyki_druzyny(druzyna1['zdobyte'], druzyna1['stracone'], mecze)
    stat2 = oblicz_statystyki_druzyny(druzyna2['zdobyte'], druzyna2['stracone'], mecze)
    return stat1, stat2

# Przykład użycia
if __name__ == "__main__":
    druzyna1 = {'zdobyte': 30, 'stracone': 20}
    druzyna2 = {'zdobyte': 25, 'stracone': 15}
    mecze = 10

    stat1, stat2 = analiza_statystyczna(druzyna1, druzyna2, mecze)
    print("Statystyki Drużyny 1:", stat1)
    print("Statystyki Drużyny 2:", stat2)

    X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, n_redundant=5, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = train_models(X_train, y_train)
    predictions = predict_with_models(models, X_test)

    print("\nOceny modeli:")
    for model_name, preds in predictions.items():
        accuracy = accuracy_score(y_test, preds)
        print(f"{model_name}: {accuracy:.2f}")

    team1_lambda = stat1["zdobyte"]
    team2_lambda = stat2["zdobyte"]
    team1_avg_conceded = stat1["stracone"]
    team2_avg_conceded = stat2["stracone"]

    plot_results(predictions, team1_lambda, team2_lambda, team1_avg_conceded, team2_avg_conceded)
