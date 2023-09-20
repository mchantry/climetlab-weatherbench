#!/usr/bin/env python3
# (C) Copyright 2022 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
from __future__ import annotations

import climetlab as cml
from climetlab import Dataset
from climetlab.decorators import normalize

__version__ = "0.1.2"

URL = "https://object-store.os-api.cci1.ecmwf.int"

PATTERN = "{url}/weatherbench/" "{parameter}_{year}_5.625deg.nc"


class Main(Dataset):
    name = "WeatherBench"
    home_page = "https://github.com/pangeo-data/WeatherBench"
    # The licence is the licence of the data (not the licence of the plugin)
    licence = "-"
    documentation = "-"
    citation = (
        "@article{rasp2020weatherbench,"
        "title={WeatherBench: A benchmark dataset for data-driven weather forecasting},"
        "author={Rasp, Stephan and Dueben, Peter D and Scher, Sebastian and Weyn,"
        "Jonathan A and Mouatadid, Soukayna and Thuerey, Nils},"
        "journal={arXiv preprint arXiv:2002.00469},"
        "year={2020}}"
    )

    # These are the terms of use of the data (not the licence of the plugin)
    terms_of_use = (
        "By downloading data from this dataset, "
        "you agree to the terms and conditions defined at "
        "https://github.com/mchantry/"
        "climetlab-weatherbench/"
        "blob/main/LICENSE. "
        "If you do not agree with such terms, do not download the data. "
    )

    dataset = None

    @normalize("parameter", ["geopotential_500hPa", "temperature_850hPa"])
    def __init__(self, year, parameter):
        request = dict(parameter=parameter, url=URL, year=year)
        self.source = cml.load_source("url-pattern", PATTERN, request)
