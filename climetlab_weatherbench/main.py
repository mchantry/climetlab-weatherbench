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

__version__ = "0.2.0"

URL = "https://storage.ecmwf.europeanweather.cloud"

PATTERN = "{url}/WeatherBench/{parameter}hPa_{year}_5.625deg.nc"


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

    @normalize("parameter", ["geopotential_500", "temperature_850"])
    def __init__(self, year, parameter, grid=5.625):
        request = dict(parameter=parameter, url=URL, year=year)

        if grid == 5.625 and year in range(1979, 2019):
            self.source = cml.load_source("url-pattern", PATTERN, request)
        else:
            request = {
                "product_type": "reanalysis",
                "format": "netcdf",
                "year": f"{year}",
                "month": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                ],
                "day": [
                    "01",
                    "02",
                    "03",
                    "04",
                    "05",
                    "06",
                    "07",
                    "08",
                    "09",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                    "20",
                    "21",
                    "22",
                    "23",
                    "24",
                    "25",
                    "26",
                    "27",
                    "28",
                    "29",
                    "30",
                    "31",
                ],
                "time": [
                    "00:00",
                    "06:00",
                    "12:00",
                    "18:00",
                ],
                "grid": [grid, grid],
            }
            if "_" in parameter:
                param_split = parameter.split("_")
                variable = param_split[0]
                level = param_split[1]
                request["pressure_level"] = level
                cds_source = "reanalysis-era5-pressure-levels"
            else:
                variable = parameter
                cds_source = "reanalysis-era5-single-levels"
            request["variable"] = variable

            self.source = cml.load_source("cds", cds_source, request)
        return
