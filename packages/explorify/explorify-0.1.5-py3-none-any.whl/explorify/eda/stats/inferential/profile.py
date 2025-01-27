#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Explorify                                                                           #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.12                                                                             #
# Filename   : /explorify/eda/stats/inferential/profile.py                                         #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/variancexplained/explorify                                       #
# ------------------------------------------------------------------------------------------------ #
# Created    : Tuesday August 22nd 2023 07:45:44 pm                                                #
# Modified   : Sunday January 26th 2025 05:53:26 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Optional

from explorify import DataClass
from explorify.utils.io import IOService

# ------------------------------------------------------------------------------------------------ #
STAT_CONFIG = "config/stats.yml"


# ------------------------------------------------------------------------------------------------ #
@dataclass
class StatTestProfile(DataClass):
    """Abstract base class defining the interface for statistical tests.

    Interface inspired by: https://doc.dataiku.com/dss/latest/statistics/tests.html
    """

    id: str
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    statistic: Optional[str] = field(default=None)
    analysis: Optional[str] = field(default=None)  # one of ANALYSIS_TYPES
    hypothesis: Optional[str] = field(default=None)  # One of HYPOTHESIS_TYPES
    H0: Optional[str] = field(default=None)
    parametric: Optional[bool] = field(default=None)
    min_sample_size: Optional[int] = field(default=None)
    assumptions: Optional[str] = field(default=None)
    use_when: Optional[str] = field(default=None)
    a_type: Optional[str] = field(
        default=None
    )  # Variable type in ['categorical','numeric']
    b_type: Optional[str] = field(default=None)

    @classmethod
    def create(cls, id) -> StatTestProfile:
        """Loads the values from the statistical tests file"""
        profiles = IOService.read(STAT_CONFIG)
        profile = profiles[id]
        fieldlist = {f.name for f in fields(cls) if f.init}
        filtered_dict = {k: v for k, v in profile.items() if k in fieldlist}
        filtered_dict["id"] = id
        return cls(**filtered_dict)
