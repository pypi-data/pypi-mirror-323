import numpy as np
from sklearn.linear_model import BayesianRidge
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
import math
import scipy.integrate as integrate
from scipy.special import gamma, gammainc, factorial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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
        'mlp': MLPClassifier().fit(X_train, y_train),
        'logistic_regression': LogisticRegression().fit(X_train, y_train),
        'ridge_classifier': RidgeClassifier().fit(X_train, y_train),
        'lda': LinearDiscriminantAnalysis().fit(X_train, y_train),
        'qda': QuadraticDiscriminantAnalysis().fit(X_train, y_train)
    }
    return models

# Predykcja wyników
def predict_with_models(models, X_test):
    predictions = {model_name: model.predict(X_test) for model_name, model in models.items()}
    return predictions

# Rysowanie wyników
def plot_results(predictions, team1_lambda, team2_lambda, team1_avg_conceded, team2_avg_conceded):
    fig, axs = plt.subplots(15, 3, figsize=(15, 45))
    events = ['Liczba goli', 'Rzuty rożne', 'Spalone', 'Kartki', 'Kontuzje', 'Faule', 'Rzuty karne',
              'Posiadanie piłki', 'Strzały na bramkę', 'Skuteczność strzałów', 'Podania', 'Przejęcia piłki',
              'Interwencje bramkarzy', 'Ofiary fauli', 'Celne podania']
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
        ax1.set_xticks(x1)
        ax1.set_xticklabels(['Drużyna 1', 'Drużyna 2'])
        ax1.set_xlabel('Drużyna')
        ax1.set_ylabel('Zdobyte')
        ax1.set_zlabel('Stracone')
    plt.tight_layout()
    plt.show()

# Stała Eulera
euler_const = 0.5772156649

# Funkcje matematyczne
def gamma_function(x):
    if int(x) == x and x <= 0:
        raise ValueError("Funkcja gamma nie jest zdefiniowana dla niepozytywnych liczb całkowitych.")
    return gamma(x)

def beta_function(x, a, b):
    numerator = gamma(a) * gamma(b)
    denominator = gamma(a + b)
    return numerator / denominator

def poisson_probability(k, lmbda):
    return (lmbda ** k * math.exp(-lmbda)) / factorial(k)

# Funkcje statystyczne
def expected_value(alpha):
    return alpha

def median(alpha):
    return math.floor(alpha + 1 / 3 - 0.02 / alpha)

def variance(alpha):
    return alpha

def entropy(alpha):
    term1 = 0.5 * math.log(2 * math.pi * alpha)
    term2 = -1 / (12 * alpha)
    term3 = -1 / (24 * alpha ** 2)
    term4 = -19 / (360 * alpha ** 3)
    return term1 + term2 + term3 + term4

# Obliczenia sportowe
def oblicz_srednia_zdobytych_goli(gole_zdobyte, bezposr_spotkania):
    return gole_zdobyte / bezposr_spotkania

def oblicz_srednia_straconych_goli(gole_stracone, bezposr_spotkania):
    return gole_stracone / bezposr_spotkania

def oblicz_wynik_druzyny(gole_zdobyte, gole_stracone, bezposr_spotkania):
    srednia_zdobytych = oblicz_srednia_zdobytych_goli(gole_zdobyte, bezposr_spotkania)
    srednia_straconych = oblicz_srednia_straconych_goli(gole_stracone, bezposr_spotkania)
    return srednia_zdobytych, srednia_straconych

def okresl_typ_meczu(srednia1_zdobytych, srednia2_zdobytych):
    if srednia1_zdobytych > srednia2_zdobytych:
        return "Wygrany typ 1"
    elif srednia1_zdobytych < srednia2_zdobytych:
        return "Wygrany typ 2"
    else:
        return "Remis"

# Funkcje rysujące wykresy
def rysuj_wykresy(srednia1_zdobytych, srednia1_straconych, srednia2_zdobytych, srednia2_straconych):
    labels = ['Drużyna 1 Zdobyte', 'Drużyna 1 Stracone', 'Drużyna 2 Zdobyte', 'Drużyna 2 Stracone']
    values = [srednia1_zdobytych, srednia1_straconych, srednia2_zdobytych, srednia2_straconych]
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    axs[0, 0].plot(labels, values, marker='o')
    axs[0, 0].set_title('Wykres Liniowy')
    axs[0, 1].bar(labels, values, color=['blue', 'red', 'green', 'orange'])
    axs[0, 1].set_title('Wykres Słupkowy')
    plt.show()

# Tabela gamma
def tabela_wartosci_gamma(start, end):
    values = np.linspace(start, end, 30)
    return [(x, gamma_function(x)) for x in values]

def drukuj_tabele_gamma(start, end):
    table = tabela_wartosci_gamma(start, end)
    print("Tabela Gamma(x):")
    for x, gamma_val in table:
        print(f"{x:.2f} | {gamma_val:.2f}")

# Przykład obliczeń
x = 2.5
k = 17
lmbda = 12
print(f"Gamma({x}) = {gamma_function(x)}")
print(f"P(X = {k}) dla lambda = {lmbda} wynosi {poisson_probability(k, lmbda)}")

# Obliczenia pomocnicze
def calculate_poisson_cdf(k, lmbda):
    return sum(poisson_probability(i, lmbda) for i in range(0, k + 1))

def calculate_poisson_pmf(k, lmbda):
    return poisson_probability(k, lmbda)

# Obliczenia na danych drużyn
def oblicz_statystyki_druzyny(gole_zdobyte, gole_stracone, mecze):
    srednia_zdobytych = gole_zdobyte / mecze
    srednia_straconych = gole_stracone / mecze
    return {
        'średnia zdobytych': srednia_zdobytych,
        'średnia straconych': srednia_straconych
    }

# Funkcja główna dla analizy statystycznej
def analiza_statystyczna(druzyna1, druzyna2, mecze):
    statystyki1 = oblicz_statystyki_druzyny(druzyna1['zdobyte'], druzyna1['stracone'], mecze)
    statystyki2 = oblicz_statystyki_druzyny(druzyna2['zdobyte'], druzyna2['stracone'], mecze)
    print("Statystyki Drużyny 1:", statystyki1)
    print("Statystyki Drużyny 2:", statystyki2)
    return statystyki1, statystyki2

# Przykładowe dane wejściowe
druzyna1 = {'zdobyte': 30, 'stracone': 20}
druzyna2 = {'zdobyte': 25, 'stracone': 15}
mecze = 10

# Analiza statystyczna drużyn
statystyki1, statystyki2 = analiza_statystyczna(druzyna1, druzyna2, mecze)

# Tworzenie wizualizacji wyników
rysuj_wykresy(statystyki1['średnia zdobytych'], statystyki1['średnia straconych'],
              statystyki2['średnia zdobytych'], statystyki2['średnia straconych'])