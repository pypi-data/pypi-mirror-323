def t_5(var):
    if var == 1:
        text = """Ряд совместных наблюдений независимых нормально распределенных случайных величин X и Y, описывающих некоторый финансовый показатель двух фирм, задан двумерной выборкой:
{(-199.76, -175.45); (-219.72, -194.67);

ALPHA_MEAN = 0.01  # Уровень значимости для теста средних
APLHA_VARIANCE = 0.05  # Уровень значимости для теста дисперсий

import pandas as pd
import numpy as np
from scipy.stats import pearsonr, ttest_ind, f

raw_data = [(-195.996, -166.5), (-165.653, -176.5),]

data = pd.DataFrame(raw_data, columns=["A", "B"])
data = data.replace("NA", np.nan).dropna()

correlation, _ = pearsonr(data["A"], data["B"])
print(f"Коэффициент корреляции Пирсона: {correlation:.20f}")

t_stat, p_value_ttest = ttest_ind(data["A"], data["B"], equal_var=False, alternative='less')
print(f"P-значение (t-тест Уэлча): {p_value_ttest:.20f}")
      
result_mean_test = int(p_value_ttest < ALPHA_MEAN)
print(f"Результат теста средних (0.01): {result_mean_test}")

var_a = np.var(data["A"], ddof=1)
var_b = np.var(data["B"], ddof=1)
df_a = len(data["A"]) - 1
df_b = len(data["B"]) - 1

if var_a > var_b:
    f_stat = var_a / var_b
    p_value_f_test = 2 * min(f.cdf(f_stat, df_a, df_b), 1 - f.cdf(f_stat, df_a, df_b))
else:
    f_stat = var_b / var_a
    p_value_f_test = 2 * min(f.cdf(f_stat, df_b, df_a), 1 - f.cdf(f_stat, df_b, df_a))
print(f"P-значение (F-тест): {p_value_f_test:.20f}")


result_var_test = int(p_value_f_test < APLHA_VARIANCE)
print(f"Результат теста дисперсий (0.05): {result_var_test}")
        """
    if var == 2:
        text = """Независимые наблюдения нормально распределенной случайной величины X, описывающей приращение стоимости типового контракта страховой фирмы, представлены в виде выборки:
{-194.69; -253.453; NA

ALPHA_MEAN = 0.9  # Уровень значимости для доверительного интервала для среднего
ALPHA_VAR = 0.9   # Уровень значимости для доверительного интервала для дисперсии

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

data = np.array([223.9, 228.8797, None])

count_data = len(data)
print("Объём исходной выборки:", count_data)

missing_count = np.sum([x is None for x in data])
print("Количество пропущенных значений:", missing_count)

cleaned_data = np.array([x for x in data if x is not None])
sorted_data = np.sort(cleaned_data)
cleaned_size = len(sorted_data)
print("Объем очищенной выборки:", cleaned_size)

mean_value = sorted_data.mean()
print("Среднее значение:", mean_value)

std_dev = np.std(sorted_data, ddof=1)
print("Стандартное отклонение (исправленное):", std_dev)

variance = np.var(sorted_data, ddof=1)
print("Несмещенная дисперсия:", variance)

q1 = np.percentile(sorted_data, 25)
median = np.median(sorted_data)
q3 = np.percentile(sorted_data, 75)
print("Первая квартиль:", q1)
print("Медиана:", median)
print("Третья квартиль:", q3)

max_value = sorted_data.max()
print("Максимальное значение:", max_value)

min_value = sorted_data.min()
print("Минимальное значение:", min_value)

range_value = max_value - min_value
print("Размах выборки:", range_value)

kurtosis = stats.kurtosis(sorted_data, bias=False)
print("Эксцесс:", kurtosis)

skewness = stats.skew(sorted_data)
print("Коэффициент асимметрии:", skewness)

sample_error = stats.sem(sorted_data)
print("Ошибка выборки:", sample_error)

confidence_mean = stats.t.interval(
    ALPHA_MEAN, cleaned_size - 1, loc=mean_value, scale=std_dev / np.sqrt(cleaned_size)
)
print(f"Левая граница {ALPHA_MEAN}-доверительного интервала для E(X):", confidence_mean[0])
print(f"Правая граница {ALPHA_MEAN}-доверительного интервала для E(X):", confidence_mean[1])

chi2_lower = stats.chi2.ppf((1 - ALPHA_VAR) / 2, cleaned_size - 1)
chi2_upper = stats.chi2.ppf(1 - (1 - ALPHA_VAR) / 2, cleaned_size - 1)
confidence_variance = (
    (cleaned_size - 1) * variance / chi2_upper,
    (cleaned_size - 1) * variance / chi2_lower
)
print(f"Левая граница {ALPHA_VAR}-доверительного интервала для Var(X):", confidence_variance[0])
print(f"Правая граница {ALPHA_VAR}-доверительного интервала для Var(X):", confidence_variance[1])

Q1 = np.percentile(sorted_data, 25)
Q3 = np.percentile(sorted_data, 75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers_below = np.sum(sorted_data < lower_bound)
outliers_above = np.sum(sorted_data > upper_bound)

print("Нижняя граница:", lower_bound)
print("Верхняя граница:", upper_bound)
print("Количество выбросов ниже нормы:", outliers_below)
print("Количество выбросов выше нормы:", outliers_above)
    """
    if var == 3:
        text = """По результатам социологического исследования ответы респондентов на определенный вопрос анкеты представлены в виде выборки:
{NA; Unkn; Less; More; Norm;

ALPHA = 0.1  # уровень значимости для критерия Хи-квадрат
CONFIDENCE_LEVEL = 0.99  # уровень доверия для интервала
ANSWER_KOLICHESTVO = 'A' # что ищем, когда ищем КОЛИЧЕСТВО (Есть не в каждом варианте)
ANSWER_DOLYA = 'B' # что ищем, когда ищем ДОЛЮ

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm
import matplotlib.pyplot as plt

# Вставить данные (могут быть другие слова\буквы)

sample = [
    'C', 'D', 'C' ... ... ... 'A', 'A', 'D'
]

cleaned_sample = [x for x in sample if x != 'NA']
na_count = len(sample) - len(cleaned_sample)

unique_answers = set(cleaned_sample)
num_unique_answers = len(unique_answers)
print(f"Количество различных вариантов ответов: {num_unique_answers}")

sample_size = len(cleaned_sample)
print(f"Объем очищенной выборки: {sample_size}")

num_na = na_count
print(f"Количество пропущенных данных 'NA': {num_na}")

a_count = cleaned_sample.count(ANSWER_KOLICHESTVO)
print(f"Количество респондентов, которые дали ответ 'A': {a_count}")

y_count = cleaned_sample.count(ANSWER_DOLYA)
y_ratio = y_count / sample_size
print(f"Доля респондентов, которые дали ответ '{ANSWER_DOLYA}': {y_ratio:.4f}")

z = norm.ppf(1 - (1 - CONFIDENCE_LEVEL) / 2)
se = np.sqrt(y_ratio * (1 - y_ratio) / sample_size)
lower_bound = y_ratio - z * se
upper_bound = y_ratio + z * se
print(f"Правая граница {CONFIDENCE_LEVEL} доверительного интервала: {upper_bound:.4f}")
print(f"Левая граница {CONFIDENCE_LEVEL} доверительного интервала: {lower_bound:.4f}")

observed_counts = pd.Series(cleaned_sample).value_counts().values
expected_counts = [sample_size / num_unique_answers] * num_unique_answers
chi2_stat = sum((obs - exp) ** 2 / exp for obs, exp in zip(observed_counts, expected_counts))
df = num_unique_answers - 1
critical_value = chi2.ppf(1 - ALPHA, df)
reject_null = int(chi2_stat > critical_value)
print(f"Критическое значение статистики хи-квадрат: {critical_value:.4f}")
print(f"Количество степеней свободы: {df}")
print(f"Наблюдаемое значение хи-квадрат: {chi2_stat:.4f}")
print(f"Есть основания отвергнуть гипотезу: {reject_null}")

plt.figure(figsize=(8, 5))
plt.hist(cleaned_sample, bins=len(unique_answers), alpha=0.7, color='blue', rwidth=0.85)
plt.xlabel('Ответы респондентов')
plt.ylabel('Частота')
plt.title('Гистограмма очищенной выборки')
plt.grid(axis='y')
plt.show()
    """
    return text
