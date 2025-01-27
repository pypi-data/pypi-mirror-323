def t_5_3(var=1):
    if var == 1:
        text = """1. По результатам социологического исследования ответы респондентов на определенный вопрос анкеты представлены в виде выборки:
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
    if var == 2:
        text = """2. По результатам социологического исследования ответы респондентов на определенный вопрос анкеты представлены в виде выборки:
        {M; M; M; M; F; F; M; F; M; M; Child;

        import pandas as pd
        
        data_str = '{M; M; M; M; F; F; M; F; M; M; Child; F; M; M; Child; Child; Child; F; NA; M; Child; Child; F; M; M; F; Child; F; NA; M; M; M; M; M; Child; M; F; M; F; M; M; M; Child; M; F; M; Child; Child; F; Child; Child; M; F; M; Child; Child; M; M; Child; M; M; Child; Child; Child; Child; NA; M; Child; F; M; NA; M; Child; NA; M; F; M; F; M; M; Child; Child; Child; M; M; M; M; M; M; M; F; F; M; M; M; Child; M; M; M; Child; NA; M; F; Child; M; M; M; Child; M; M; M; Child; M; Child; F; M; Child; Child; M; Child; M; M; F; Child; Child; NA; M; M; F; F; M; Child; M; NA; M; M; F; F; M; M; M; F; M; Child; M; NA; M; Child; NA; F; M; NA; Child; Child; F; M; M; NA; Child; Child; F; M; F; M; Child; F; F; Child; M; M; M; F; F; M; F; M; M; M; M; F; NA; M; M; Child; Child; M; Child; M; Child; M; M; NA; M; Child; NA; NA; Child; M; Child; M; M; NA; Child; M; Child; M; Child; NA; M; M; Child; F; F; F; Child; Child; NA; F; M; M; Child; Child; M; M; NA; M; NA; F; M; Child; Child; NA; Child; NA; F; M; Child; F; F; Child; Child; M; Child; NA; M; M; Child; NA; M; F; M; M; M; M; Child; M; Child; Child; M; F; F; F; Child; M; Child; Child; M; Child; M; M; Child; M; F; M; M; M; F; Child; Child; Child; M; F; NA; M; M; M; M; F; M; M; M; F; M; M; M; M; Child; M; M; Child; Child; M; M; M; Child; M; F; F; M; M; M; M; F; M; M; M; M; F; M; M}'
        data= data_str.replace('{', '').replace('}', '').split('; ')
        df = pd.DataFrame(data=data, columns=['A'])
        
        # Очистка выборки от пропусков
        cleaned_df = df[df.A != 'NA']
        
        # Количество уникальных значений
        unique_values = cleaned_df['A'].unique()
        print(f"Варианты ответов: {len(unique_values)}")
        
        # Размер очищенной выборки
        clean_size = len(cleaned_df)
        print(f"Объем очищенной выборки: {clean_size}")
        
        # Количество пропусков
        na_count = sum(df['A'] == 'NA')
        print(f"Пропуски: {na_count}")
        
        # Доля ответов "F"
        f_responses = cleaned_df.query("A == 'F'")
        f_ratio = len(f_responses) / clean_size
        print(f"Доля ответов 'F': {f_ratio}")
        
        from statsmodels.stats.proportion import proportion_confint
        
        # Вычисление доверительных интервалов
        ci_low, ci_up = proportion_confint(count=len(f_responses), nobs=clean_size, alpha=0.05)
        print(f"Правая граница 0.95-доверительного интервала: {ci_up}")
        
        print(f"Левая граница 0.95-доверительного интервала: {ci_low}")
        
        from scipy.stats import chi2
        
        # Число степеней свободы
        degrees_of_freedom = len(unique_values) - 1
        
        # Уровень значимости
        alpha = 0.1
        
        # Критическое значение
        critical_value = chi2.ppf(1 - alpha, degrees_of_freedom)
        print(f"Критическое значение статистики Хи-квадрат: {critical_value}")
        
        print(f"Степени свободы: {degrees_of_freedom}")
        
        from scipy.stats import chisquare
        
        # Подсчет частот каждого ответа
        observed_freqs = cleaned_df['A'].value_counts().values
        
        # Равномерное распределение
        expected_freqs = [clean_size / len(unique_values)] * len(unique_values)
        
        # Вычисление статистики Хи-квадрат
        chi2_stat, p_val = chisquare(observed_freqs, expected_freqs)
        print(f"Наблюдаемое значение Хи-квадрат: {chi2_stat}")
        
        if chi2_stat > critical_value:
            print("Есть основания отвергнуть гипотезу о равновероятном распределении ответов.")
        else:
            print("Нет оснований отвергнуть гипотезу о равновероятном распределении ответов.")
        
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        cleaned_df['A'].hist()
        plt.title('Распределение ответов респондентов')
        plt.xlabel('Вариант ответа')
        plt.ylabel('Количество ответов')
        plt.show()
        """
    if var == 3:
        text = """3. По результатам социологического исследования ответы респондентов на определенный вопрос анкеты представлены в виде выборки:
        {NA; Unkn; Less; More; Norm;

        import pandas as pd
        from scipy.stats import chi2, binomtest
        import numpy as np
        import matplotlib.pyplot as plt
        
        data_str = '{More; More; Unkn; More; Less; Norm; More; More; NA; More; Unkn; Less; NA; Norm; More; Less; Less; Unkn; NA; NA; Less; Unkn; More; Norm; Less; Less; More; NA; Unkn; More; More; Unkn; Norm; Unkn; NA; NA; Less; Less; More; Unkn; Norm; Norm; NA; Less; Norm; Less; Norm; Norm; More; NA; Norm; More; More; Unkn; Less; Less; NA; More; More; Unkn; NA; Norm; Less; Norm; Unkn; Unkn; Norm; Norm; Unkn; More; More; More; Norm; Less; Less; Less; Unkn; Unkn; NA; NA; NA; Unkn; Unkn; Unkn; Unkn; Norm; More; More; More; Unkn; Less; Unkn; Less; More; Unkn; More; Unkn; Norm; Less; Norm; Unkn; Unkn; Unkn; Unkn; Less; Unkn; Unkn; Less; Less; More; More; Unkn; Unkn; More; Less; Unkn; Unkn; Norm; Unkn; Norm; Less; Unkn; NA; Norm; NA; NA; NA; Norm; Unkn; Less; Norm; Norm; Unkn; Unkn; More; More; Unkn; Less; Unkn; NA; Less; NA; Less; More; NA; Unkn; More; More; More; More; NA; NA; Norm; NA; NA; More; Norm; Unkn; Less; Unkn; Unkn; Unkn; NA; More; Less; NA; Norm; More; Unkn; Unkn; More; Less; More; Unkn; More; Norm; Less; More; More; Unkn; Unkn; More; NA; Unkn; Norm; NA; Unkn; Unkn; More; More; Unkn; Less; Norm; More; Unkn; More; More; Unkn; Unkn; Less; Unkn; Less; Unkn; Norm; Unkn; Unkn; More; Unkn; Unkn; More; Unkn; NA; NA; NA; Unkn; Norm; More; Unkn; NA; Unkn; NA; Norm; Unkn; More; Less; Unkn; More; More; More; Unkn; Unkn; NA; Norm; Unkn; NA; Norm; Less; More; Unkn; Unkn; Less; More; Unkn; Norm; More; Unkn; Unkn; Unkn; More; Norm; Norm; More; Norm; Less; Unkn; Norm; More; NA; NA; Less; Unkn; Unkn; Unkn; NA; Unkn; More; NA; Unkn; Unkn; Norm; Less; Unkn; More; More; More; Unkn; Unkn; Unkn; Unkn; NA; Norm; Unkn; Unkn; More; Less; Unkn; Norm; Norm; More; NA; Less; Unkn; Less; Unkn; Less; Less; Norm; Unkn; NA; Norm}'
        data_list = data_str.replace('{', '').replace('}', '').split('; ')
        df = pd.DataFrame(data=data_list, columns=['A'])
        
        cleaned_df = df[df.A != 'NA']
        
        # Часть 1: Объем очищенной от "NA" выборки
        print(f"Вопрос 1: {len(cleaned_df)}")
        
        # Часть 2: Количество различных вариантов ответов респондентов, встречающихся в очищенной выборке
        print(f"Вопрос 2: {cleaned_df['A'].nunique()}")
        
        # Часть 3: Количество респондентов, которые дали ответ "X"
        print(f"Вопрос 3: {(cleaned_df['A'] == 'Less').sum()}")
        
        # Часть 4: Доля респондентов, которые дали ответ "Y"
        print(f"Вопрос 4: {(cleaned_df['A'] == 'More').mean()}")
        
        # Часть 5: Левая граница 0.99-доверительного интервала для истинной доли ответов "Y"
        y_responses = cleaned_df[cleaned_df['A'] == 'More']
        
        from statsmodels.stats.proportion import proportion_confint
        
        ci_low, ci_up = proportion_confint(count=len(y_responses), nobs=len(cleaned_df), alpha=0.01)
        
        print(f"Левая граница 0.99-доверительного интервала: {ci_low}")
        
        # Часть 6: Правая граница 0.99-доверительного интервала для истинной доли ответов "Y"
        print(f"Правая граница 0.99-доверительного интервала: {ci_up}")
        
        # Часть 7: Количество степеней свободы
        k = cleaned_df['A'].nunique() - 1
        print(f"Вопрос 7: {k}")
        
        # Часть 8: Критическое значение статистики Хи-квадрат
        alpha = 0.01
        crit_value = chi2.ppf(1 - alpha, k)
        print(f"Вопрос 8: {crit_value}")
        
        # Часть 9: Наблюдаемое значение Хи-квадрат
        observed_values = cleaned_df['A'].value_counts().values
        expected_values = len(cleaned_df) / observed_values.size * np.ones_like(observed_values)
        chi_squared_stat = ((observed_values - expected_values)**2 / expected_values).sum()
        print(f"Вопрос 9: {chi_squared_stat}")
        
        # Часть 10: Проверка гипотезы о равновероятном распределении ответов
        if chi_squared_stat > crit_value:
            print(f"Вопрос 10: 1")
        else:
            print(f"Вопрос 10: 0")
        
        # Часть 11: Гистограмма для исходной выборки, очищенной от "NA"
        cleaned_df['A'].hist()
        plt.show()
        """

    return text
