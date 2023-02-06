#!/usr/bin/env python3
# (C) Copyright 2022 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
from __future__ import annotations
from .common import ALL_DAYS, ALL_MONTHS

import logging

import climetlab as cml
from climetlab import Dataset
from climetlab.decorators import normalize
from climetlab.sources.multi import MultiSource

LOG = logging.getLogger(__name__)

__version__ = "0.2.0"

URL = "https://storage.ecmwf.europeanweather.cloud"

TIMESTEPS = {6: ["00:00", "06:00", "12:00", "18:00"]}
GRIDS = {
    0.1: '0.1/0.1',
    0.4: '0.4/0.4',
    1.4: '1.4/1.4',
    2.8: '2.8/2.8',
    5.625: '5.625/5.625',
}
LEVELS = [850, 500]
PARAMETERS = {}
CONSTANT_PARAMETERS = {
    # 'constants':'constants',
}
SINGLE_LEVEL_PARAMETERS = {
    'total_cloud_cover': 'single-level',
    'total_precipitation': 'single-level',
    '10m_u_component_of_wind': 'single-level',
    '10m_v_component_of_wind': 'single-level',
    '2m_temperature': 'single-level',
}
NON_SINGLE_LEVEL_PARAMETERS = {
    'geopotential': 'pressure-level',
    'potential_vorticity': 'pressure-level',
    'relative_humidity': 'pressure-level',
    'specific_humidity': 'pressure-level',
    'temperature': 'pressure-level',
    'toa_incident_solar_radiation': 'pressure-level',
    'u_component_of_wind': 'pressure-level',
    'v_component_of_wind': 'pressure-level',
    'vorticity': 'pressure-level',
}
PARAMETERS.update(CONSTANT_PARAMETERS)
PARAMETERS.update(SINGLE_LEVEL_PARAMETERS)
PARAMETERS.update(NON_SINGLE_LEVEL_PARAMETERS)


PARAMETER_LEVELS = list(SINGLE_LEVEL_PARAMETERS.keys()) + list(CONSTANT_PARAMETERS.keys()) + \
    [f"{p}_{l}" for p in NON_SINGLE_LEVEL_PARAMETERS for l in LEVELS]


class Extended(Dataset):
    name = "weather-bench-extended"
    home_page = "-"
    # The licence is the licence of the data (not the licence of the plugin)
    licence = "-"
    documentation = "-"
    citation = '-'

    # These are the terms of use of the data (not the licence of the plugin)
    terms_of_use = (
        "By downloading data from this dataset, "
        "you agree to the terms and conditions defined at "
        "https://github.com/mchantry/climetlab-weatherbench/blob/main/LICENSE. "
        "If you do not agree with such terms, do not download the data. "
    )

    @normalize(
        "parameter_level",
        PARAMETER_LEVELS,
        aliases={f"{p_l}Hpa": p_l for p_l in PARAMETER_LEVELS},
        multiple=True,
    )
    @normalize("parameter", list(PARAMETERS.keys()), aliases={"t2m": "2m_temperature"}, multiple=True)
    @normalize("level", type=int, multiple=True)  # @normalize("level", list(LEVELS.keys()), multiple=True)
    @normalize("year", list(range(1979, 2022)), multiple=True)
    @normalize("grid", list(GRIDS.keys()))  # [5.625, 0.1, 0.25, 1.4])
    @normalize("timestep", list(TIMESTEPS.keys()), aliases={'3h': 3, '6h': 6})
    def __init__(self, parameter_level=None, year=None, grid=5.625, timestep=6, parameter=None, level=None):

        print(self.parse_parameter_level(parameter_level, parameter, level))
        
        sources = []
        for param, level in self.parse_parameter_level(parameter_level, parameter, level):
            sources.append(
                MultiSource(
                    [self.build_source(y, param, level, grid, timestep) for y in year],
                    #merger="concat(dim=time)",
                ).mutate()
            )

        # Merging manually latter because we need special option to merge
        self.source = MultiSource(sources).mutate()
        # self.source = MultiSource(sources, merge='merge()')

    def parse_parameter_level(self, parameter_level=None, parameter=None, level=None):

        if parameter_level:
            msg = f"Use parameter_level or (parameter, level), not both. {(parameter_level, parameter, level)}"
            assert parameter is None, msg
            assert level is None,  msg

            out = []
            for p_l in parameter_level:
                if p_l in SINGLE_LEVEL_PARAMETERS or p_l in CONSTANT_PARAMETERS:
                    out.append((p_l, None))
                    continue
                lst = p_l.split("_")
                param = '_'.join(lst[:-1])
                level = lst[-1]
                if level.lower().endswith('hpa'):
                    level = level[:-3]
                level = int(level)
                assert param in NON_SINGLE_LEVEL_PARAMETERS, param
                out.append((param, level))
            return out

        if not parameter:
            raise ValueError("missing parameter")

        if level:
            for p in parameter:
                assert p in NON_SINGLE_LEVEL_PARAMETERS, p
            return [(p, l) for p in parameter for l in level]

        for p in parameter:
            assert p in SINGLE_LEVEL_PARAMETERS or p in CONSTANT_PARAMETERS, p
        return [(p, None) for p in parameter]


    def to_xarray(self, **kwargs):
        options = dict(xarray_open_mfdataset_kwargs=dict(compat="override"))
        options.update(kwargs)
        ds = self.source.to_xarray(**options)

        if "level" in ds.variables:
            ds = ds.drop("level")
        return ds

class WeatherbenchExtendedMARS(Extended):

    def build_source(self, year, param, level, grid, timestep):
        timestep = TIMESTEPS[timestep]
        request = {
            "product_type": "reanalysis",
            "year": f"{year}",
            "month": ALL_MONTHS,
            "day": ALL_DAYS,
            "time": timestep,
            "grid": GRIDS[grid],
        }

        request["param"] = param
        if level:
            dataset_name = "era5-complete"
            request["pressure_level"] = level
            request["levtype"] = 'pressure'
        else:
            dataset_name = "era5-complete"
            request["levtype"] = 'sfc'

        source = cml.load_source("mars", dataset_name, request)
        source = source.order_by('date', 'param', 'level')
        return source

class WeatherbenchExtendedCDS(Extended):

    def build_source(self, year, param, level, grid, timestep):
        timestep = TIMESTEPS[timestep]
        request = {
            "product_type": "reanalysis",
            "year": f"{year}",
            "month": ALL_MONTHS,
            "day": ALL_DAYS,
            "time": timestep,
            "grid": GRIDS[grid],
        }

        request["param"] = param
        if level:
            dataset_name = "reanalysis-era5-pressure-levels"
            request["pressure_level"] = level
        else:
            dataset_name = "reanalysis-era5-single-levels"

        source = cml.load_source("cds", dataset_name, request)
        source = source.order_by('date', 'param', 'level')
        return source

WeatherbenchExtended = WeatherbenchExtendedCDS