#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Explorify                                                                           #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.12                                                                             #
# Filename   : /explorify/eda/regression/simple.py                                                 #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john@variancexplained.com                                                           #
# URL        : https://github.com/variancexplained/explorify                                       #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday June 12th 2024 11:51:03 pm                                                #
# Modified   : Sunday January 26th 2025 05:31:58 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2024 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm

from explorify.eda.regression.base import RegressionAnalyzer, RegressionResult


# ------------------------------------------------------------------------------------------------ #
@dataclass
class SimpleRegressionResult(RegressionResult):
    """Simple regression result"""

    name: str = "Simple Linear Regression"
    a_name: Optional[str] = field(default=None)
    b_name: Optional[str] = field(default=None)
    intercept: Optional[float] = field(default=None)
    intercept_ci: Optional[float] = field(default=None)
    intercept_stderr: Optional[float] = field(default=None)
    slope: Optional[float] = field(default=None)
    slope_ci: Optional[float] = field(default=None)
    slope_stderr: Optional[float] = field(default=None)
    df_num: Optional[float] = field(default=None)
    df_den: Optional[float] = field(default=None)
    fvalue: Optional[float] = field(default=None)
    rvalue: Optional[float] = field(default=None)
    pvalue: Optional[float] = field(default=None)
    alpha: Optional[float] = field(default=None)
    params: tuple = field(default_factory=tuple)

    @property
    def report(self) -> str:
        """Reports results in APA Style"""
        result = f"A Simple Linear Regression analysis was conducted to evaluate the extent to which {self.a_name} could predict {self.b_name}."
        influence = "increased" if self.slope > 0 else "decreased"  # pragma: no cover
        fsignificance = (
            "significantly better fit"
            if self.pvalue < self.alpha
            else "non significant difference in fit"
        )
        improved = (
            "significantly improved"
            if self.pvalue < self.alpha
            else "didn't significantly improve"
        )
        significance = (
            " A significant regression was"
            if self.pvalue < self.alpha
            else "A non significant regression was"
        )

        result += (
            significance
            + f" found (F({self.df_num}, {self.df_den})={self.fvalue}, {self._report_pvalue(np.abs(self.pvalue))})."
            + r"The $R^2$ was "
            + f"{self._report_rvalue(self.rvalue)}, indicating that {self.a_name} explained appoximately {self._report_rvalue(self.rvalue)}% of the variance in {self.b_name}. The equation for the regression is as follows:\n"
            + f"{self.b_name} = {self.intercept} + {self.slope}*({self.a_name})."
            + f" That is, for each unit of increase in {self.a_name}, the predicted {self.b_name} {influence} by approximately {round(np.abs(self.slope),2)} {self.b_name} units of measurement."
            + f" Furthermore, an F-Test was conducted to compare the full and restricted models. The F-test indicated that the full model provided a {fsignificance} to the data than did the restricted model, (F({self.df_num}, {self.df_den})={self._report_statistic(self.fvalue)}, {self._report_pvalue(self.pvalue)}). These results suggest that the predictor variable {self.a_name} {improved} the prediction of {self.b_name}."
        )
        return result


# ------------------------------------------------------------------------------------------------ #
class SimpleRegressionAnalyzer(RegressionAnalyzer):
    def __init__(
        self,
        a_name: str,
        b_name: str,
        data: pd.DataFrame,
        alpha: float = 0.05,
        **kwargs,
    ) -> None:
        super().__init__()
        self._a_name = a_name
        self._b_name = b_name
        self._data = data
        self._kwargs = kwargs
        self._alpha = alpha
        self._result = None

    @property
    def result(self) -> SimpleRegressionResult:
        """Returns the Cramer's V Result object."""
        return self._result

    def run(self) -> None:
        """Performs the statistical test and creates a result object."""

        result = sm.OLS(
            endog=self._data[self._b_name],
            exog=sm.add_constant(self._data[self._a_name]),
            **self._kwargs,
        ).fit()
        restricted = sm.OLS(
            endog=self._data[self._b_name],
            exog=sm.add_constant(np.ones(len(self._data))),
        ).fit()
        f_test_result = result.compare_f_test(restricted)
        fvalue = f_test_result[0]
        pvalue = f_test_result[1]
        df_num = f_test_result[2]
        df_den = result.df_resid

        # Create the result object.
        self._result = SimpleRegressionResult(
            a_name=self._a_name,
            b_name=self._b_name,
            intercept=result.params.iloc[0],
            intercept_ci=f"Intercept: {result.params.iloc[0]} +/- {result.bse.iloc[0]}",
            intercept_stderr=result.bse.iloc[0],
            slope=result.params[1],
            slope_ci=f"Slope: {result.params.iloc[1]} +/- {result.bse.iloc[1]}",
            slope_stderr=result.bse.iloc[1],
            df_num=df_num,
            df_den=df_den,
            rvalue=result.rsquared,
            fvalue=fvalue,
            pvalue=pvalue,
            alpha=self._alpha,
        )
