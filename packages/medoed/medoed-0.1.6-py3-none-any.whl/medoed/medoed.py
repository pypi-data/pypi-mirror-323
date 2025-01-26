import multiprocessing as mp
import os
from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import scipy.stats as ss
from otvertka import handle_outliers
from pydantic import BaseModel, Field, field_validator
from statsmodels.stats.power import tt_ind_solve_power
from tqdm import tqdm


class MDECalculatorConfig(BaseModel):
    """
    Configuration model for the MDECalculator class.

    Parameters
    ----------
    pre_experiment_data : pd.DataFrame
        Input DataFrame containing pre-experiment data
    date_column : str
        Name of the column containing dates
    metrics : List[str]
        List of metric names to analyze
    historical_data : Optional[pd.DataFrame], optional
        Input DataFrame containing historical data, by default None
    strata : Optional[List[str]], optional
        List of columns to use for stratification, by default None
    alpha : float, optional
        Significance level, by default 0.05
    power : float, optional
        Statistical power, by default 0.8
    outliers_handling_method : Optional[str], optional
        Method for handling outliers ('replace_threshold', 'replace_median', 'drop'), by default None
    outliers_threshold_quantile : Optional[float], optional
        Quantile threshold for outlier detection (0-1), by default None
    outliers_type : Optional[str], optional
        Type of outliers to handle ('upper', 'lower', 'two-sided'), by default 'upper'
    test_days : int, optional
        Number of days to analyze, by default 90
    sample_size : Optional[int], optional
        Average number of daily installs or observations, by default None

    Returns
    -------
    MDECalculatorConfig
        Validated configuration object for MDECalculator

    Raises
    ------
    ValueError
        If outliers_handling_method is not one of [None, "replace_threshold", "replace_median", "drop"]
        If outliers_threshold_quantile is not between 0 and 1
        If outliers_type is not one of ["upper", "lower", "two-sided"]
        If metrics are not present in DataFrame columns
        If sample_size is not positive
    """

    pre_experiment_data: pd.DataFrame
    date_column: str
    metrics: List[str]
    historical_data: Optional[pd.DataFrame] = None
    strata: Optional[List[str]] = None
    alpha: float = Field(0.05, ge=0, le=1)
    power: float = Field(0.8, ge=0, le=1)
    outliers_handling_method: Optional[str] = None
    outliers_threshold_quantile: Optional[float] = None
    outliers_type: Optional[str] = None
    test_days: int = Field(90, gt=0)
    sample_size: Optional[int] = None

    @field_validator("outliers_handling_method")
    @classmethod
    def validate_outliers_handling_method(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["replace_threshold", "replace_median", "drop"]:
            raise ValueError(
                'outliers_handling_method must be None, "replace_threshold", "replace_median" or "drop"'
            )
        return v

    @field_validator("outliers_threshold_quantile")
    @classmethod
    def validate_outliers_threshold_quantile(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0 < v < 1):
            raise ValueError("outliers_threshold_quantile must be None or between 0 and 1")
        return v

    @field_validator("outliers_type")
    @classmethod
    def validate_outliers_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["upper", "lower", "two-sided"]:
            raise ValueError('outliers_type must be "upper", "lower" or "two-sided"')
        return v

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, v: List[str], info) -> List[str]:
        df = info.data.get("pre_experiment_data")
        df_historical = info.data.get("historical_data")

        if df is not None and not all(metric in df.columns for metric in v):
            raise ValueError("All metrics must be present in pre-experiment DataFrame columns")

        if df_historical is not None and not all(metric in df_historical.columns for metric in v):
            raise ValueError("All metrics must be present in historical DataFrame columns")

        return v

    @field_validator("sample_size")
    @classmethod
    def validate_sample_size(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("sample_size must be positive")
        return v

    model_config = {"arbitrary_types_allowed": True}


class MDECalculator:
    """
    Calculator for Minimum Detectable Effect (MDE) in A/B tests.

    Calculates MDE for both binary and continuous metrics, with support for
    stratification and outlier handling.

    Parameters
    ----------
    pre_experiment_data : pd.DataFrame
        Input DataFrame containing pre-experiment data
    date_column : str
        Name of the column containing dates
    metrics : List[str]
        List of metric names to analyze
    historical_data : Optional[pd.DataFrame], optional
        Input DataFrame containing historical data, by default None
    strata : Optional[List[str]], optional
        List of columns to use for stratification, by default None
    alpha : float, optional
        Significance level, by default 0.05
    power : float, optional
        Statistical power, by default 0.8
    outliers_handling_method : Optional[str], optional
        Method for handling outliers ('replace_threshold', 'replace_median', 'drop'), by default None
    outliers_threshold_quantile : Optional[float], optional
        Quantile threshold for outlier detection (0-1), by default None
    outliers_type : Optional[str], optional
        Type of outliers to handle ('upper', 'lower', 'two-sided'), by default 'upper'
    test_days : int, optional
        Number of days to analyze, by default 90
    sample_size : Optional[int], optional
        Average number of daily installs or observations, by default None

    Examples
    --------
    >>> calculator = MDECalculator(
    ...     pre_experiment_data=df_pre_experiment,
    ...     date_column='date',
    ...     metrics=['revenue'],
    ...     historical_data=df_historical,
    ...     strata=['country'],
    ...     alpha=0.05,
    ...     power=0.8,
    ...     outliers_handling_method='replace_threshold',
    ...     outliers_threshold_quantile=0.995,
    ...     outliers_type='upper',
    ...     test_days=30,
    ...     sample_size=1000
    ... )
    >>> results = calculator.calculate()
    """

    def __init__(self, **kwargs):
        config = MDECalculatorConfig(**kwargs)
        self.pre_experiment_data = config.pre_experiment_data
        self.date_column = config.date_column
        self.metrics = config.metrics
        self.historical_data = config.historical_data
        self.strata = config.strata
        self.alpha = config.alpha
        self.power = config.power
        self.outliers_handling_method = config.outliers_handling_method
        self.outliers_threshold_quantile = config.outliers_threshold_quantile
        self.outliers_type = config.outliers_type
        self.test_days = config.test_days
        self.sample_size = self._get_sample_size(config.sample_size)

    def _get_sample_size(self, sample_size: int = None) -> int:
        """
        Calculate or return the average number of daily installs.

        Parameters
        ----------
        sample_size : int, optional
            Predefined number of daily installs or observations, by default None

        Returns
        -------
        int
            Average number of daily installs
        """
        if sample_size is not None:
            return sample_size

        mean_d7_obs = (
            self.pre_experiment_data
                .groupby(self.date_column)
                .size()
                .to_frame()
                .sort_values(self.date_column)
                .tail(7)
                .mean()
                .iloc[0]
        )

        return int(mean_d7_obs // 2)

    def _is_binary_metric(self, metric: str) -> bool:
        """
        Check if a metric is binary (0/1 values only).

        Parameters
        ----------
        metric : str
            Name of the metric to check

        Returns
        -------
        bool
            True if metric is binary, False otherwise
        """
        unique_values = self.pre_experiment_data[metric].nunique()
        return unique_values == 2 and set(self.pre_experiment_data[metric].unique()).issubset({0, 1})

    def _is_stratified_metric(self) -> bool:
        """
        Check if the metric analysis requires stratification.

        Returns
        -------
        bool
            True if both historical data and stratification columns are defined
        """
        return self.historical_data is not None and len(self.strata) > 0

    def _get_strat_weights(self, df: pd.DataFrame, strat: str) -> pd.Series:
        """
        Calculate the weights of strata based on their proportion in the dataset.

        Parameters
        ----------
        df : pd.DataFrame
            The input DataFrame containing the data to be analyzed
        strat : str
            The name of the column containing stratification values

        Returns
        -------
        pd.Series
            Series with strata as index and corresponding weights as values
        """
        strat_weights = df[strat].value_counts() / df[strat].count()
        strat_weights = (
            strat_weights.to_frame().reset_index().rename(columns={"count": "strat_weight"})
        )
        return strat_weights

    def _prepare_stratification_weights(
        self, historical_data: pd.DataFrame, pre_experiment_data: pd.DataFrame
    ) -> tuple[dict, pd.DataFrame]:
        """
        Perform post-stratification on pre-experiment data using historical data.

        Parameters
        ----------
        historical_data : pd.DataFrame
            Historical data used for deriving stratum weights
        pre_experiment_data : pd.DataFrame
            Pre-experiment data to be stratified

        Returns
        -------
        tuple[dict, pd.DataFrame]
            Dictionary of stratification weights and adjusted pre-experiment DataFrame
        """
        df_historical = historical_data.copy()
        df_pre_experiment = pre_experiment_data.copy()

        for strat in self.strata:
            unique_values = (
                df_historical[strat].value_counts().to_frame().reset_index()[strat].tolist()
            )
            df_pre_experiment[strat] = df_pre_experiment[strat].apply(
                lambda x: x if x in unique_values else f"other_{strat}"
            )
            df_historical[strat] = df_historical[strat].apply(
                lambda x: x if x in unique_values else f"other_{strat}"
            )

        df_historical["strat"] = df_historical[self.strata].agg(" | ".join, axis=1)
        df_pre_experiment["strat"] = df_pre_experiment[self.strata].agg(" | ".join, axis=1)

        df_strat_weights = self._get_strat_weights(df=df_historical, strat="strat")
        weights_dict = df_strat_weights.set_index("strat")["strat_weight"].to_dict()

        missing_strata = set(df_pre_experiment["strat"]) - set(weights_dict.keys())
        if missing_strata:
            for strat in missing_strata:
                weights_dict[strat] = 0

        df_pre_experiment = pd.merge(
            df_pre_experiment, df_strat_weights, on="strat", how="left"
        ).fillna({"strat_weight": 0})

        return weights_dict, df_pre_experiment

    def _calc_stratified_mean(
        self, df: pd.DataFrame, strat: str, metric: str, weights: dict
    ) -> float:
        """
        Calculate weighted stratified mean for a metric.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame
        strat : str
            Stratification column name
        metric : str
            Metric column name
        weights : dict
            Dictionary of stratum weights

        Returns
        -------
        float
            Weighted stratified mean
        """
        strat_mean = df.groupby(strat)[metric].mean()
        return (strat_mean * pd.Series(weights)).sum()

    def _calc_stratified_variance(
        self, df: pd.DataFrame, strat: str, metric: str, weights: dict
    ) -> float:
        """
        Calculate weighted stratified variance for a metric.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame
        strat : str
            Stratification column name
        metric : str
            Metric column name
        weights : dict
            Dictionary of stratum weights

        Returns
        -------
        float
            Weighted stratified variance
        """
        strat_var = df.groupby(strat)[metric].var().fillna(0)
        return (strat_var * pd.Series(weights)).sum()

    def _calc_evan_miller_mde(
        self, base_rate: float, sample_size: int, alpha: float, power: float
    ) -> float:
        """
        Calculate MDE using Evan Miller's method for binary metrics.

        Parameters
        ----------
        base_rate : float
            Base conversion rate in control group
        sample_size : int
            Total sample size for both groups
        alpha : float, optional
            Significance level, by default None (uses instance value)
        power : float, optional
            Statistical power, by default None (uses instance value)

        Returns
        -------
        float
            Minimum detectable effect in absolute terms
        """
        alpha = alpha or self.alpha
        power = power or self.power

        t_alpha2 = ss.norm.ppf(1.0 - alpha / 2)
        t_beta = ss.norm.ppf(power)

        left = 0.0001
        right = 1 - base_rate

        for _ in range(50):
            delta = (left + right) / 2
            sd1 = np.sqrt(2 * base_rate * (1.0 - base_rate))
            sd2 = np.sqrt(
                base_rate * (1.0 - base_rate) + (base_rate + delta) * (1.0 - base_rate - delta)
            )
            required_n = (t_alpha2 * sd1 + t_beta * sd2) ** 2 / (delta * delta)

            if required_n > sample_size:
                left = delta
            else:
                right = delta

        return (left + right) / 2

    def _calc_binary_mde(self, metric: str, sample_size: int) -> float:
        """
        Calculate MDE for a binary metric.

        Parameters
        ----------
        metric : str
            Name of the binary metric
        sample_size : int
            Total sample size

        Returns
        -------
        float
            Calculated MDE value
        """
        base_rate = float(self.pre_experiment_data[metric].mean())
        return self._calc_evan_miller_mde(
            base_rate=base_rate, sample_size=sample_size, alpha=self.alpha, power=self.power
        )

    def _calc_continuous_mde(self, metric: str, sample_size: int) -> float:
        """
        Calculate MDE for a continuous metric.

        Parameters
        ----------
        metric : str
            Name of the continuous metric
        sample_size : int
            One group's sample size

        Returns
        -------
        float
            Calculated MDE as a relative change
        """
        should_handle_outliers = (
            self.outliers_handling_method is not None
            or self.outliers_threshold_quantile is not None
            or self.outliers_type is not None
        )

        if should_handle_outliers:
            method = self.outliers_handling_method or "replace_threshold"
            quantile = self.outliers_threshold_quantile or 0.995
            outlier_type = self.outliers_type or "upper"

            clean_data = handle_outliers(
                df=self.pre_experiment_data,
                target_column=metric,
                threshold_quantile=quantile,
                handling_method=method,
                outlier_type=outlier_type,
            )
        else:
            clean_data = self.pre_experiment_data

        mean = clean_data[metric].mean()
        std_dev = clean_data[metric].std()

        min_effect_size = tt_ind_solve_power(
            nobs1=sample_size,
            effect_size=None,
            alpha=self.alpha,
            power=self.power,
            ratio=1.0,
            alternative="two-sided",
        )

        absolute_change = min_effect_size * std_dev
        relative_mde = absolute_change / mean
        return relative_mde

    def _calc_stratified_mde(self, metric: str, sample_size: int) -> float:
        """
        Calculate MDE for a continuous metric using stratification.

        Parameters
        ----------
        metric : str
            Name of the continuous metric
        sample_size : int
            Total sample size

        Returns
        -------
        float
            Calculated MDE as a relative change
        """
        should_handle_outliers = (
            self.outliers_handling_method is not None
            or self.outliers_threshold_quantile is not None
            or self.outliers_type is not None
        )

        if should_handle_outliers:
            method = self.outliers_handling_method or "replace_threshold"
            quantile = self.outliers_threshold_quantile or 0.995
            outlier_type = self.outliers_type or "upper"

            df_historical = handle_outliers(
                df=self.historical_data,
                target_column=metric,
                threshold_quantile=quantile,
                handling_method=method,
                outlier_type=outlier_type,
            )
            df_pre_experiment = handle_outliers(
                df=self.pre_experiment_data,
                target_column=metric,
                threshold_quantile=quantile,
                handling_method=method,
                outlier_type=outlier_type,
            )
        else:
            df_historical = self.historical_data.copy()
            df_pre_experiment = self.pre_experiment_data.copy()

        weights_dict, df_pre_experiment = self._prepare_stratification_weights(
            historical_data=df_historical, pre_experiment_data=df_pre_experiment
        )

        mean = self._calc_stratified_mean(
            df=df_pre_experiment, strat="strat", metric=metric, weights=weights_dict
        )
        std_dev = np.sqrt(
            self._calc_stratified_variance(
                df=df_pre_experiment, strat="strat", metric=metric, weights=weights_dict
            )
        )

        if std_dev == 0:
            return 0.0

        min_effect_size = tt_ind_solve_power(
            nobs1=sample_size,
            effect_size=None,
            alpha=self.alpha,
            power=self.power,
            ratio=1.0,
            alternative="two-sided",
        )

        absolute_change = min_effect_size * std_dev
        relative_mde = absolute_change / mean if mean != 0 else float("inf")
        return relative_mde

    def _calculate_day_metrics(self, day: int) -> dict:
        """
        Calculate MDE for all metrics for a specific day.

        Parameters
        ----------
        day : int
            Day number

        Returns
        -------
        dict
            Dictionary containing day results
        """
        sample_size = day * self.sample_size
        day_results = {"day": day, "sample_size": sample_size}

        for metric in self.metrics:
            if self._is_binary_metric(metric):
                mde = self._calc_binary_mde(metric, sample_size)
            elif self._is_stratified_metric():
                mde = self._calc_stratified_mde(metric, sample_size)
            else:
                mde = self._calc_continuous_mde(metric, sample_size)

            day_results[metric] = round(mde * 100, 2)  # Convert to percentage

        return day_results

    def calculate(self, n_processes: int = None) -> pd.DataFrame:
        """
        Calculate MDE for all metrics across specified test days using parallel processing.

        Parameters
        ----------
        n_processes : int, optional
            Number of processes to use. If None, uses CPU count - 1

        Returns
        -------
        pd.DataFrame
            DataFrame containing MDE values for each metric and day,
            with columns: ['day', 'sample_size', '{metric}', ...]
        """
        if n_processes is None:
            n_processes = max(1, os.cpu_count() - 1)

        days = range(1, self.test_days + 1)

        with mp.Pool(processes=n_processes) as pool:
            results = list(
                tqdm(
                    pool.imap(self._calculate_day_metrics, days),
                    total=self.test_days,
                    desc="Calculating MDE",
                )
            )

        df_results = pd.DataFrame(results)

        column_order = ["day", "sample_size"] + self.metrics

        return df_results[column_order]

    @staticmethod
    def create_mde_plot(
        results: pd.DataFrame, template: str = "plotly_dark", title: str = "MDE"
    ) -> px.line:
        """
        Create a line plot visualizing MDE results for all metrics.

        Parameters
        ----------
        results : pd.DataFrame
            DataFrame with MDE calculation results from calculate() method
        template : str, optional
            Plotly template name, by default 'plotly_dark'
        title : str, optional
            Plot title, by default 'MDE'

        Returns
        -------
        px.line
            Plotly figure object that can be further customized or displayed
        """
        df_plot = (
            results.drop(columns=["sample_size"])
            .melt(id_vars=["day"])
            .rename(columns={"variable": "metric", "value": "mde"})
        )

        fig = px.line(df_plot, x="day", y="mde", title=title, template=template, color="metric")

        return fig
