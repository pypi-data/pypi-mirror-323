#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Explorify                                                                           #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.10                                                                             #
# Filename   : /explorify/eda/stats/inferential/gof.py                                             #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/variancexplained/explorify                                       #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday June 6th 2023 01:45:05 am                                                   #
# Modified   : Sunday January 26th 2025 05:44:56 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
from dependency_injector.wiring import Provide, inject
from scipy import stats

from explorify.container import VisualizeContainer
from explorify.eda.stats.inferential.base import StatisticalTest, StatTestResult
from explorify.eda.stats.inferential.profile import StatTestProfile
from explorify.eda.visualize.visualizer import Visualizer


# ------------------------------------------------------------------------------------------------ #
#                                     TEST RESULT                                                  #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class KSTestResult(StatTestResult):
    """Encapsulates the hypothesis test results."""

    name: str = "Kolmogorov-Smirnov Test"
    a_name: Optional[str] = field(default=None)
    b_name: Optional[str] = field(default=None)
    data: Optional[pd.DataFrame] = field(default=None)
    n: Optional[int] = field(default=None)
    advisory: Optional[str] = field(default=None)

    @inject
    def __post_init__(
        self, visualizer: Visualizer = Provide[VisualizeContainer.visualizer]
    ) -> None:
        self.visualizer = visualizer

    def plot(self) -> None:  # pragma: no cover
        self.visualizer.kstestplot(
            statistic=self.value,
            n=len(self._data[self.a_name]),
            result=self.result,
            alpha=self.alpha,
        )

    @property
    def report(self) -> str:
        """Reports the result in APA style."""
        result = f"Kolmogorov-Smirnov Goodness of Fit\nD({self.n})={round(self.value,4)}, p={round(self.pvalue,3)}"
        return result


# ------------------------------------------------------------------------------------------------ #
#                                          TEST                                                    #
# ------------------------------------------------------------------------------------------------ #
class KSTest(StatisticalTest):
    """Performs the (one-sample or two-sample) Kolmogorov-Smirnov test for goodness of fit.

    The one-sample test compares the underlying distribution F(x) of a sample against a given
    distribution G(x). The two-sample test compares the underlying distributions of
    two independent samples. Both tests are valid only for continuous distributions.

    Args:
        a_name (str): Name of a continuous column in the dataset
        b_name (str): Name of a continuous column in the dataset
        data (pd.DataFrame): DataFrame containing the two columns.

    """

    __id = "kstest"

    def __init__(
        self,
        a_name: str,
        b_name: str,
        data: pd.DataFrame,
        alpha: float = 0.05,
    ) -> None:
        super().__init__()
        self._a_name = a_name
        self._b_name = b_name
        self._data = data
        self._alpha = alpha
        self._profile = StatTestProfile.create(self.__id)
        self._result = None

    @property
    def profile(self) -> StatTestProfile:
        """Returns the statistical test profile."""
        return self._profile

    @property
    def result(self) -> StatTestResult:
        """Returns a Statistical Test Result object."""
        return self._result

    def run(self) -> None:
        """Performs the statistical test and creates a result object."""

        n = len(self._data)

        # Conduct the two-sided ks test
        try:
            result = stats.kstest(
                rvs=self._data[self._a_name].values,
                cdf=self._data[self._b_name].values,
                alternative="two-sided",
            )
        except KeyError:
            result = stats.kstest(
                rvs=self._data[self._a_name].values,
                cdf=self._b_name,
                alternative="two-sided",
            )
        except Exception as e:  # pragma: no cover
            msg = f"Invalid arguments {self._a_name}, {self._b_name}\n{e}"
            self._logger.exception(msg)
            raise

        advisory = None
        if len(self._data[self._a_name]) < 50:
            advisory = "Note: The Kolmogorov-Smirnov Test requires a sample size N > 50. For smaller sample sizes, the Shapiro-Wilk test should be considered."
        if len(self._data[self._a_name]) > 1000:
            advisory = "Note: The Kolmogorov-Smirnov Test on large sample sizes may lead to rejections of the null hypothesis that are statistically significant, yet practically insignificant."

        # Create the result object.
        self._result = KSTestResult(
            H0=self._profile.H0,
            statistic=self._profile.statistic,
            hypothesis=self._profile.hypothesis,
            value=result.statistic,
            pvalue=result.pvalue,
            a_name=self._a_name,
            b_name=self._b_name,
            data=self._data,
            n=n,
            advisory=advisory,
            alpha=self._alpha,
        )


# ------------------------------------------------------------------------------------------------ #
#                                     TEST RESULT                                                  #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class ChiSquareGOFTestResult(StatTestResult):
    """Encapsulates the hypothesis test results."""

    name: str = "Chisquare Goodness of Fit Test"
    categorical_variable: Optional[str] = field(default=None)
    f_actual: Optional[str] = field(default=None)
    f_exp: Optional[str] = field(default=None)
    data: Optional[pd.DataFrame] = field(default=None)
    n: Optional[int] = field(default=None)
    dof: Optional[int] = field(default=None)
    n: Optional[int] = field(default=None)

    @inject
    def __post_init__(
        self, visualizer: Visualizer = Provide[VisualizeContainer.visualizer]
    ) -> None:
        self.visualizer = visualizer

    def plot(
        self, title: Optional[str] = field(default=None)
    ) -> None:  # pragma: no cover
        title = (
            title
            or f"X\u00b2 Goodness of Fit Plot\nX\u00b2({self.dof}, N={self.n}) = {self._report_statistic(statistic=self.value)}, p={self._report_pvalue(pvalue=self.pvalue)}"
        )
        self.visualizer.x2testplot(
            statistic=self.value,
            dof=self.dof,
            alpha=self.alpha,
            title=title,
        )

    @property
    def report(self) -> str:
        """Reports the result in APA style."""
        if self.pvalue > self.alpha:
            result = "was not"
        else:
            result = "was"
        report = f"A X\u00b2 Goodness of Fit test was performed to evaluate whether the distribution of {self.categorical_variable} followed that of the general population. The distribution of {self.categorical_variable} {result} signficantly different from that of the general population, X\u00b2({self.dof}, N={self.n}) = {self._report_statistic(statistic=self.value)}, p={self._report_pvalue(pvalue=self.pvalue)}"
        return report


# ------------------------------------------------------------------------------------------------ #
#                                          TEST                                                    #
# ------------------------------------------------------------------------------------------------ #
class ChiSquareGOFTest(StatisticalTest):
    """
    Perform a Chi-Square Goodness of Fit (GOF) test for categorical variables
    to assess whether the observed distribution matches the expected distribution.


    Properties:
        profile (StatTestProfile): Returns the statistical test profile.
        result (Optional[ChiSquareGOFTestResult]): Returns the result object
            of the Chi-Square GOF test.

    Methods:
        run() -> None:
            Performs the Chi-Square GOF test based on the specified parameters.
            Calculates chi-square statistic and p-value, and creates a result object.
    Args:
        categorical_variable (str): Name of the categorical variable being tested.
        f_actual (str): Name of the column in `data` containing actual frequencies or counts.
        f_exp (str): Name of the column in `data` containing expected frequencies or counts.
        data (pd.DataFrame): DataFrame containing the data for the test.
        normalize_to_observed_freq (bool): Flag indicating whether to normalize expected
            and actual frequencies to proportions.
        alpha (float, optional): Significance level for the test (default is 0.05).

    Notes:
        This class assumes the use of scipy.stats.chisquare for computing the test statistics.
        The `run()` method calculates expected and actual counts or proportions,
        performs the chi-square test, and creates a `ChiSquareGOFTestResult` object with
        relevant statistical information.
    """

    __id = "x2gof"

    def __init__(
        self,
        categorical_variable: str,
        f_actual: str,
        f_exp: str,
        data: pd.DataFrame,
        normalize_to_observed_freq: bool,
        alpha: float = 0.05,
    ) -> None:
        """
        Initializes the ChiSquareGOFTest instance."""
        super().__init__()
        self._categorical_variable = categorical_variable
        self._f_actual = f_actual
        self._f_exp = f_exp
        self._data = data
        self._normalize_to_observed_freq = normalize_to_observed_freq
        self._alpha = alpha
        self._profile = StatTestProfile.create(self.__id)
        self._result = None

    @property
    def profile(self) -> StatTestProfile:
        """Returns the statistical test profile."""
        return self._profile

    @property
    def result(self) -> Optional[ChiSquareGOFTestResult]:
        """Returns the result object of the Chi-Square GOF test."""
        return self._result

    def run(self) -> None:
        """
        Performs the Chi-Square GOF test based on the specified parameters.
        Calculates chi-square statistic and p-value, and creates a result object.
        """
        if self._normalize_to_observed_freq:
            expected_proportions = (
                self._data[self._f_exp] / self._data[self._f_exp].sum()
            )
            actual_proportions = (
                self._data[self._f_actual] / self._data[self._f_actual].sum()
            )
            total_count = self._data[self._f_actual].sum()

            actual_counts = actual_proportions * total_count
            expected_counts = expected_proportions * total_count

            x2, p_value = stats.chisquare(f_obs=actual_counts, f_exp=expected_counts)

        else:
            x2, p_value = stats.chisquare(
                f_obs=self._data[self._f_actual], f_exp=self._data[self._f_exp]
            )

        dof = len(self._data[self._f_exp]) - 1
        n = self._data[self._f_actual].sum()

        # Create the result object.
        self._result = ChiSquareGOFTestResult(
            H0=self._profile.H0,
            statistic=self._profile.statistic,
            hypothesis=self._profile.hypothesis,
            value=x2,
            pvalue=p_value,
            categorical_variable=self._categorical_variable,
            f_actual=self._f_actual,
            f_exp=self._f_exp,
            dof=dof,
            n=n,
            data=self._data,
            alpha=self._alpha,
        )
