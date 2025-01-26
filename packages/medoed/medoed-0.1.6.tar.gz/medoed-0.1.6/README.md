# medoed

![medoed](./assets/logo.png)

Библиотека для расчета минимального определяемого эффекта (MDE) в A/B тестах.

## Установка

```bash
pip install medoed
```

## Пример использования

```python
from medoed import MDECalculator

mde_calculator = MDECalculator(
    pre_experiment_data=pre_experiment_data,
    date_field='install_date',
    metrics=['revenue', 'retention'],
    historical_data=historical_data,
    strata=['geo', 'os'],
    alpha=0.05,
    power=0.8,
    outliers_handling_method='replace_threshold',
    outliers_threshold_quantile=0.995,
    outlier_type='upper',
    test_days=30,
    sample_size=10000
)

df_mde = mde_calculator.calculate(n_processes=8)
fig = mde_calculator.create_mde_plot(df_mde)
fig.show()
```

## Требования

- Python 3.8+
- pandas 1.3+
- numpy 1.20+
- scipy 1.7+
- statsmodels 0.13+
- otvertka 0.1.6+
- tqdm 4.65+

## Лицензия

MIT
