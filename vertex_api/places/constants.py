ADDRESS_COMPONENT_TYPES = (
    'street_address',  # indicates a precise street address.
    'route',  # indicates a named route (such as "US 101").
    'intersection',  # indicates a major intersection, usually of two major roads.
    'political',
    # indicates a political entity.
    # Usually, this type indicates a polygon of some civil administration.
    'country',
    # indicates the national political entity, and
    # is typically the highest order type returned by the Geocoder.
    'administrative_area_level_1',
    # indicates a first-order civil entity below the country level.
    # Within the United States, these administrative levels are states.
    # Not all nations exhibit these administrative levels.
    # In most cases, administrative_area_level_1 short names will closely match
    # ISO 3166-2 subdivisions and other widely circulated lists;
    # however this is not guaranteed as our geocoding results are based on a variety of
    # signals and location data.
    'administrative_area_level_2',
    # indicates a second-order civil entity below the country level.
    # Within the United States, these administrative levels are counties.
    # Not all nations exhibit these administrative levels.
    'administrative_area_level_3',
    # indicates a third-order civil entity below the country level.
    # This type indicates a minor civil division.
    # Not all nations exhibit these administrative levels.
    'administrative_area_level_4',
    # indicates a fourth-order civil entity below the country level.
    # This type indicates a minor civil division.
    # Not all nations exhibit these administrative levels.
    'administrative_area_level_5',
    # indicates a fifth-order civil entity below the country level.
    # This type indicates a minor civil division.
    # Not all nations exhibit these administrative levels.
    'colloquial_area',  # indicates a commonly-used alternative name for the entity.
    'locality',  # indicates an incorporated city or town political entity.
    'sublocality',
    # indicates a first-order civil entity below a locality.
    'neighborhood',  # indicates a named neighborhood
    'premise',
    # indicates a named location, usually a building or collection of buildings with a common name
    'subpremise',
    # indicates a first-order entity below a named location,
    # usually a singular building within a collection of buildings with a common name
    'postal_code',  # indicates a postal code as used to address postal mail within the country.
    'natural_feature',  # indicates a prominent natural feature.
    'airport',  # indicates an airport.
    'park',  # indicates a named park.
    'point_of_interest',
    # indicates a named point of interest.
    # Typically, these "POI"s are prominent local entities that don't easily fit in
    # another category, such as "Empire State Building" or "Statue of Liberty."
)

ADDRESS_TYPES = ADDRESS_COMPONENT_TYPES + (
    'floor',  # indicates the floor of a building address.
    'establishment',  # typically indicates a place that has not yet been categorized.
    'parking',  # indicates a parking lot or parking structure.
    'post_box',  # indicates a specific postal box.
    'postal_town',
    # indicates a grouping of geographic areas, such as locality and sublocality,
    # used for mailing addresses in some countries.
    'room',  # indicates the room of a building address.
    'street_number',  # indicates the precise street number.
    'bus_station',
    'train_station',
    'transit_station',  # indicate the location of a bus, train or public transit stop.
)
