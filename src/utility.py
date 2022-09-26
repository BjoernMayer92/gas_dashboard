def df_to_geojson(df, properties, lat='lat', lon='lon'):
    """ Taken from https://notebook.community/captainsafia/nteract/applications/desktop/example-notebooks/pandas-to-geojson

    Args:
        df (_type_): _description_
        properties (_type_): _description_
        lat (str, optional): _description_. Defaults to 'lat'.
        lon (str, optional): _description_. Defaults to 'lon'.

    Returns:
        _type_: _description_
    """
    # create a new python dict to contain our geojson data, using geojson format
    geojson = {'type':'FeatureCollection', 'features':[]}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [row[lon],row[lat]]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]
        
        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)
    
    return geojson