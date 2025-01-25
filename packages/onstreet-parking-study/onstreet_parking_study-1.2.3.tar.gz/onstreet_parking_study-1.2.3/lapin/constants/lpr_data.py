# columns
INDEX = 'data_index'
UUID = 'uuid'
PLATE = 'plaque'
LATITUDE = 'lat'
LONGITUDE = 'lng'
SIDE_OF_CAR = 'side_of_car'
DATETIME = 'datetime'

# trips
ORIGIN_LAT = 'origin_lat'
ORIGIN_LNG = 'origin_lng'
DESTINATION_LAT = 'destination_lat'
DESTINATION_LNG = 'destination_lng'
GEOMETRY = 'geometry'

DFLT_TRJ_CONF = {
   'latitude': LATITUDE,
   'longitude': LONGITUDE,
   'datetime': DATETIME,
   'user_id': UUID
}

DFLT_LPR_CONF = {
   'plate': PLATE,
   'latitude': LATITUDE,
   'longitude': LONGITUDE,
   'datetime': DATETIME,
   'user_id': UUID,
   'side_of_car': SIDE_OF_CAR
}
