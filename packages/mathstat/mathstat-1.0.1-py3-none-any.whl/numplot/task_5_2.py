def t_5_2():
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

    return text
