""" This module provide function to post_process tennery-creek
    data after reading it raw from conf.
"""
import os
from copy import deepcopy
import pandas as pd

from lapin.constants.lpr_data import (
    DFLT_LPR_CONF,
    DFLT_TRJ_CONF
)
from lapin.constants import (LATITUDE, LONGITUDE,
                             PLATE, DATETIME,
                             PROJECT_TIMEZONE)


def vehicule_detection_post_processing(lapi, data_config):
    """_summary_

    Parameters
    ----------
    lapi : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    lapi = lapi.copy()
    # lat, lng
    lapi[LATITUDE] = lapi.geometry.y
    lapi[LONGITUDE] = lapi.geometry.x
    lapi.loc[lapi.alprLatitude == 0, LATITUDE] = 0
    lapi.loc[lapi.alprLongitude == 0, LONGITUDE] = 0

    # plate
    lapi.rename(columns={'licensePlate': PLATE}, inplace=True)
    lapi = lapi[~lapi[PLATE].isna()]

    # timestamp from utc to local
    lapi.detectionDatetime = pd.to_datetime(
        lapi.detectionDatetime,
        utc=True,
        format='ISO8601'
    )
    lapi[DATETIME] = lapi.detectionDatetime.dt.tz_convert(PROJECT_TIMEZONE)

    # reset_index
    lapi = lapi.reset_index()

    # sort
    lapi = lapi.sort_values(DATETIME)

    # rename old value
    lapi[data_config['user_id']] = lapi[data_config['user_id']].replace(
        'COMPACT2',
        'COMPACT002'
    )

    return lapi


def vehicule_post_processing(gdf, data_config):
    """_summary_

    Parameters
    ----------
    gdf : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    gdf = gdf.copy()
    gdf[LATITUDE] = gdf.geometry.y
    gdf[LONGITUDE] = gdf.geometry.x

    # timestamp from utc to local
    gdf.geolocationDatetime = pd.to_datetime(
        gdf.geolocationDatetime,
        utc=True,
        format='ISO8601'
    )
    gdf[DATETIME] = gdf.geolocationDatetime.dt.tz_convert(
        PROJECT_TIMEZONE
    )

    # sort
    gdf = gdf.sort_values(DATETIME)

    gdf[data_config['user_id']] = gdf[data_config['user_id']].replace(
        'COMPACT2',
        'COMPACT002'
    )

    return gdf


COSMOS_SETTINGS = {
    'host': os.environ.get(
        'ACCOUNT_HOST',
        ''
    ),
    'master_key': os.environ.get(
        'ACCOUNT_KEY',
        ''
    ),
    'database_id': os.environ.get(
        'COSMOS_DATABASE',
        ''
    ),
    'container_id': '',
}

COSMOS_SETTINGS_LPR = deepcopy(COSMOS_SETTINGS)
COSMOS_SETTINGS_LPR['container_id'] = os.environ.get(
    'COSMOS_CONTAINER_LPR',
    'VehiculeDetection'
)

COSMOS_SETTINGS_VEH = deepcopy(COSMOS_SETTINGS)
COSMOS_SETTINGS_VEH['container_id'] = os.environ.get(
    'COSMOS_CONTAINER_VEH',
    'SystemGeolocation'
)

# Vehicule detection
DFLT_LPR_CONF.update({'date_kwargs': {'format': 'ISO8601'}})
DFLT_LPR_CONF['user_id'] = 'alprSystemId'
DFLT_LPR_CONF['data_index'] = 'detectionId'

LPR_CONNECTION = {
    'query': """
        SELECT c.detectionDate, c.type, c.geometry, c.properties FROM c
    """,
    'dates': [],
    'date_col': 'detectionDate',
    'tdf_columns_config': DFLT_LPR_CONF,
    'cosmos_config': COSMOS_SETTINGS_LPR,
    'enable_cross_partition_query': True,
    'func': vehicule_detection_post_processing
}

# Vehicule
DFLT_TRJ_CONF.update({'date_kwargs': {'format': 'ISO8601'}})
DFLT_TRJ_CONF['user_id'] = 'alprSystemId'

VEH_CONNECTION = {
    'query': """
        SELECT c.geolocationDate, c.type, c.geometry, c.properties FROM c
    """,
    'dates': [],
    'date_col': 'geolocationDate',
    'tdf_columns_config': DFLT_TRJ_CONF,
    'cosmos_config': COSMOS_SETTINGS_VEH,
    'enable_cross_partition_query': True,
    'func': vehicule_post_processing
}