# combined_bukmacherska

combined_bukmacherska to biblioteka łącząca funkcjonalności bibliotek `bukmacherska` i `bukmacherska_crystal`.

## Funkcje

### combined_library.py

- `train_models_1(X_train, y_train)`: Trenuje zestaw modeli na danych treningowych.
- `predict_with_models_1(models, X_test)`: Wykonuje predykcje dla każdego modelu na danych testowych.
- `plot_results_1(predictions, team1_lambda, team2_lambda, team1_avg_conceded, team2_avg_conceded)`: Wizualizacja wyników za pomocą różnych typów wykresów.
- `gamma_function_1(x)`: Oblicza wartość funkcji gamma dla x.
- `beta_function_1(x, a, b)`: Oblicza wartość funkcji beta.
- `poisson_probability_1(k, lmbda)`: Oblicza prawdopodobieństwo dla rozkładu Poissona.
- `expected_value(alpha)`: Oblicza wartość oczekiwaną.
- `median(alpha)`: Oblicza medianę.
- `variance(alpha)`: Oblicza wariancję.
- `entropy(alpha)`: Oblicza entropię.
- `oblicz_srednia_zdobytych_goli(gole_zdobyte, bezposr_spotkania)`: Oblicza średnią zdobytych goli.
- `oblicz_srednia_straconych_goli(gole_stracone, bezposr_spotkania)`: Oblicza średnią straconych goli.
- `oblicz_wynik_druzyny(gole_zdobyte, gole_stracone, bezposr_spotkania)`: Oblicza wynik drużyny.
- `okresl_typ_meczu(srednia1_zdobytych, srednia2_zdobytych)`: Określa typ meczu.
- `rysuj_wykresy(srednia1_zdobytych, srednia1_straconych, srednia2_zdobytych, srednia2_straconych)`: Rysuje wykresy.
- `tabela_wartosci_gamma(start, end)`: Tworzy tabelę wartości funkcji gamma.
- `drukuj_tabele_gamma(start, end)`: Drukuje tabelę wartości funkcji gamma.
- `calculate_poisson_cdf(k, lmbda)`: Oblicza dystrybuantę rozkładu Poissona.
- `calculate_poisson_pmf(k, lmbda)`: Oblicza prawdopodobieństwo masy rozkładu Poissona.
- `oblicz_statystyki_druzyny(gole_zdobyte, gole_stracone, mecze)`: Oblicza statystyki drużyny.
- `analiza_statystyczna(druzyna1, druzyna2, mecze)`: Analizuje statystyki drużyn.

### combined_library2.py

- `train_models_2(X_train, y_train)`: Trenuje zestaw 24 różnych modeli na danych treningowych.
- `predict_with_models_2(models, X_test)`: Wykonuje predykcje dla każdego modelu na danych testowych.
- `plot_results_2(predictions, team1_lambda, team2_lambda, team1_avg_conceded, team2_avg_conceded)`: Wizualizacja wyników za pomocą różnych typów wykresów.
- `gamma_function_2(x)`: Oblicza wartość funkcji gamma dla x.
- `beta_function_2(x, a, b)`: Oblicza wartość funkcji beta.
- `poisson_probability_2(k, lmbda)`: Oblicza prawdopodobieństwo dla rozkładu Poissona.
- `analiza_statystyczna_2(druzyna1, druzyna2, mecze)`: Analizuje statystyki obu drużyn.

## Instalacja

Aby zainstalować bibliotekę, użyj poniższego polecenia:

```sh
pip install combined_bukmacherska

import combined_bukmacherska as cb

# Przykład użycia funkcji poisson_probability
beta = 2
alpha = 3
probability = cb.poisson_probability_1(beta, alpha)
print(f"Poisson Probability: {probability}")

# Trening modeli
X_train = ...
y_train = ...
models_1 = cb.train_models_1(X_train, y_train)
models_2 = cb.train_models_2(X_train, y_train)

# Predykcje
X_test = ...
predictions_1 = cb.predict_with_models_1(models_1, X_test)
predictions_2 = cb.predict_with_models_2(models_2, X_test)

# Rysowanie wykresów
cb.plot_results_1(predictions_1, team1_lambda, team2_lambda, team1_avg_conceded, team2_avg_conceded)
cb.plot_results_2(predictions_2, team1_lambda, team2_lambda, team1_avg_conceded, team2_avg_conceded)

