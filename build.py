import fiona
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt 
import seaborn as sns
import shapely
import datetime

sample = 0.05    

def get_memory_usage(df): 
    """
    Get memory usage for a dataframe
    """
    return f"{df.memory_usage(index=True).sum()//1024:,} KB"

def load_administrative_shapes(gdb):
    """
    Process humanitarian data exchange administrative shapes for Ukraine. 
    We take the most granular here, urban and hromada-level info... 
    """
    
    print(f"Opening geodatabase {gdb}...") 
    layers = fiona.listlayers(gdb)

    print(f"Enumerating layers...") 
    for i, layer in enumerate(layers): 
        admin = gpd.read_file(gdb, layer=i)
        print(" -", i, layer) 

    ukraine_urban_lyr = 3
    ukraine_hromada_lyr = 4
    ukraine_lyr = 7

    print(f"Loading urban shape data from layer {ukraine_urban_lyr}") 
    urban_gdf = gpd.read_file(gdb, layer=ukraine_urban_lyr)
    print(f"  Found {len(urban_gdf)} polygons.")

    print(f"Loading hromada shape data from layer {ukraine_hromada_lyr}") 
    hromada_gdf = gpd.read_file(gdb, layer=ukraine_hromada_lyr)
    print(f"  Found {len(hromada_gdf)} polygons.")

    print(f"Loading Ukraine shape data from layer {ukraine_lyr}") 
    ukraine_gdf = gpd.read_file(gdb, layer=ukraine_lyr)
    print(f"  Found {len(ukraine_gdf)} polygons.")

    print(f"Loaded adminstrative shapes.") 

    return urban_gdf, hromada_gdf, ukraine_gdf

def load_firms_data(shapes=None):
    """
    Import FIRMS data for all sensors. Optionally constrain the resulting dataframe by the 
    provided dataframe (uses default geometry)
    """
    
    def convert_modis_confidence(c): 
        s = 'l'
        if c > 66: 
            s = 'h' 
        elif c > 33:
            s = 'n' 

        return s
    
    firms_data = [
        { 'source':'j1v',   'path':'NASA-FIRMS/DL_FIRE_J1V-C2_519173/fire_nrt_J1V-C2_519173.shp',   '' : [] }, 
        { 'source':'j2v',   'path':'NASA-FIRMS/DL_FIRE_J2V-C2_519174/fire_nrt_J2V-C2_519174.shp',   '' : [] },
        { 'source':'sv',    'path':'NASA-FIRMS/DL_FIRE_SV-C2_519175/fire_archive_SV-C2_519175.shp', '' : [] }, 
        { 'source':'modis', 'path':'NASA-FIRMS/DL_FIRE_M-C61_519172/fire_archive_M-C61_519172.shp', '' : [] },
    ]
    
    firms_dfs = {}

    print(f"Opening FIRMS data...")
    
    for data in firms_data: 
        print(f"Reading data for {data['source']} from {data['path']}...")
        firms_dfs[data['source']] = gpd.read_file(data['path']) 
        print(f"  Found {len(firms_dfs[data['source']])} records.")

    print(f"Cleaning fire classifications...")
    firms_dfs['modis'].drop('TYPE', axis='columns', inplace=True) 
    firms_dfs['sv'].drop('TYPE', axis='columns', inplace=True) 

    print(f"Cleaning version...") 
    for name, df in firms_dfs.items(): 
        df.drop('VERSION', axis='columns', inplace=True) 

    print(f"Homogenizing detection confidences...")    
    firms_dfs['modis']['CONFIDENCE'] = firms_dfs['modis']['CONFIDENCE'].apply(convert_modis_confidence)  

    print(f"Merging data...") 
    firms_gdf = gpd.GeoDataFrame()
    for name, df in firms_dfs.items(): 
        print(f" - adding {name} records")
        firms_gdf = pd.concat([firms_gdf, df])

    if sample != 1: 
        print(f"Sampling data @ {sample*100}%")
        firms_gdf = firms_gdf.sample(frac=sample)

    def build_acq_date(d, t): 
        return pd.to_datetime(str(d.date()) + ' ' + t.zfill(4), format='%Y-%m-%d %H%M')
    
    print(f"Creating datetime field...")    
    firms_gdf['ACQ_DATETIME'] = firms_gdf.apply(
        lambda x: build_acq_date(x['ACQ_DATE'], x['ACQ_TIME']), 
        axis='columns'
        )
    
    if shapes is not None: 
        print(f"Intersecting detections with provided geometry ({len(shapes)})...")
        firms_gdf = firms_gdf.sjoin(shapes, how="inner")

    print(f"Removing unneeded administrative boundary information... ")
    firms_gdf.drop(
        [
            'index_right', 
            'ADM0_EN', 
            'ADM0_UA', 
            'ADM0_RU', 
            'ADM0_PCODE', 
            'date', 
            'validOn', 
            'validTo', 
            'AREA_SQKM', 
            'Shape_Length', 
            'Shape_Area'
        ], 
        axis='columns', 
        inplace=True
    ) 

    print(f"Loaded FIRMS data.") 

    return firms_gdf

def load_acled_data(path): 
    
    print(f"Loading ACLED data from {path}...")
    acled_df = pd.read_csv(path)
    print(f"  Found {len(acled_df)} records.")

    print(f"Converting event dates...")    
    acled_df['event_date'] = pd.to_datetime(acled_df['event_date'], format='%d %B %Y') 

    print(f"Removing events outside Ukraine...")
    acled_df = acled_df[acled_df['country'] ==  'Ukraine']

    if sample != 1: 
        print(f"Sampling data @ {sample*100}%")
        acled_df= acled_df.sample(frac=sample)

    print(f"Pruning columns... ")
    acled_df.drop(
        [
            'year', 
            'actor1', 
            'assoc_actor_1', 
            'inter1',
            'actor2', 
            'assoc_actor_2', 
            'inter2',
            'interaction', 
            'civilian_targeting', 
            'iso', 
            'region',
            'country',
            'source',
            'source_scale',
            'notes',
            'fatalities',
            'tags', 
            'timestamp',
        ], 
        axis='columns', 
        inplace=True
    ) 

    print(f"Removing low temporal precision events...")
    acled_df.drop(acled_df[acled_df.time_precision > 1].index, inplace=True)

    drop_subevents = [
        'Abduction/forced disappearance', 
        'Agreement', 
        #'Armed clash', 
        #'Air/drone strike',
        #'Shelling/artillery/missile attack', 
        #'Disrupted weapons use',
        #'Remote explosive/landmine/IED', 
        'Peaceful protest', 
        'Other',
        #'Non-state actor overtakes territory', 
        'Change to group/activity',
        #'Attack', 
        #'Grenade', 
        'Abduction/forced disappearance',
        #'Headquarters or base established', 
        #'Looting/property destruction',
        #'Arrests', 
        'Government regains territory', 
        #'Sexual violence',
        #'Protest with intervention', 
        'Suicide bomb',
        #'Non-violent transfer of territory', 
        #'Agreement', 
        #'Mob violence',
        'Excessive force against protesters', 
        'Violent demonstration'
    ]
    
    print(f"Removing non-kinetic events...")
    for subevent in drop_subevents: 
        print(f"  dropping {subevent}")
        acled_df.drop(acled_df[acled_df.sub_event_type == subevent].index, inplace=True)
    
    print(f"Creating geodataframe...")
    acled_gdf = gpd.GeoDataFrame(
        acled_df, 
        geometry = gpd.points_from_xy(acled_df.longitude, acled_df.latitude),
        crs = "EPSG:4326"
        )

    print(f"Droppping NaN rows...")
    acled_gdf.dropna(subset=['admin2', 'admin3'], inplace=True)

    print(f"Loaded ACLED data.")

    return acled_gdf

def intersect_times(firms_gdf, acled_gdf): 
    """
    Identify the window of time the provide dataframes overlap and reduce both 
    according to this window
    """               

    start = max(firms_gdf['ACQ_DATE'].min(), acled_gdf['event_date'].min())
    firms_gdf.drop(firms_gdf[firms_gdf.ACQ_DATE < start].index, inplace=True)
    acled_gdf.drop(acled_gdf[acled_gdf.event_date < start].index, inplace=True)

    end = min(firms_gdf['ACQ_DATE'].max(), acled_gdf['event_date'].max()) 
    firms_gdf.drop(firms_gdf[firms_gdf.ACQ_DATE > end].index, inplace=True)
    acled_gdf.drop(acled_gdf[acled_gdf.event_date > end].index, inplace=True)

def clean_administrative_data(urban_gdf, hromada_gdf, acled_gdf):

    print(f"Cleaning unused columns from urban shapes...") 
    urban_gdf.drop([ 
            #'ADM4_EN', 
            #'ADM4_UA', 
            'ADM4_RU', 
            'ADM4_PCODE', 
            #'ADM3_EN', 
            #'ADM3_UA',
            'ADM3_RU', 
            'ADM3_PCODE', 
            #'ADM2_EN', 
            #'ADM2_UA', 
            'ADM2_RU', 
            'ADM2_PCODE',
            #'ADM1_EN', 
            #'ADM1_UA', 
            'ADM1_RU', 
            'ADM1_PCODE', 
            'ADM0_EN', 
            'ADM0_UA',
            'ADM0_RU', 
            'ADM0_PCODE', 
            'date', 
            'validOn', 
            'validTo', 
            'AREA_SQKM',
            'Shape_Length', 
            'Shape_Area', 
        ], 
        axis='columns', 
        inplace=True)

    print(f"Cleaning unused columns from Hromada shapes...") 
    hromada_gdf.drop([ 
            #'ADM3_EN', 
            #'ADM3_UA',
            'ADM3_RU', 
            'ADM3_PCODE', 
            #'ADM2_EN', 
            #'ADM2_UA', 
            'ADM2_RU', 
            'ADM2_PCODE',
            #'ADM1_EN', 
            #'ADM1_UA', 
            'ADM1_RU', 
            'ADM1_PCODE', 
            'ADM0_EN', 
            'ADM0_UA',
            'ADM0_RU', 
            'ADM0_PCODE', 
            'date', 
            'validOn', 
            'validTo', 
            'AREA_SQKM',
            'Shape_Length', 
            'Shape_Area', 
        ], 
        axis='columns', 
        inplace=True)

    print(f"Cleaning unused columns from ACLED shapes...") 
    acled_gdf.drop([
            #'event_id_cnty',  
            #'event_date', 
            'time_precision', 
            #'disorder_type',
            #'event_type', 
            #'sub_event_type', 
            'admin1', 
            'admin2', 
            'admin3',
            #'location', 
            #'latitude', 
            #'longitude', 
            #'geo_precision', 
            #'geometry'
        ], 
        axis='columns',
        inplace=True
    )

def contextualize_events(acled_gdf, urban_gdf, hromada_gdf): 
    """
    Identify the smallest administrative divisions that the conflict events
    in the ACLED data were bounded by and emit an enriched geodataframe
    that includes the relevant polygons. 
    """    

    # Line up a maximal number of urban/city divisions as these are the most granular
    # this equates to the L4 geometry in the HDX reference data
    print("Correlating events to city-level boundaries...")
    acled_gdf = acled_gdf.sjoin(urban_gdf, how="left")
    
    # Everything that's not located in the L4 data needs to be matched to the 
    # smallest non-city adminstrative boundary (the Hromada in Ukraine)
    # probably not appropriate to call this 'rural' but suburbanrural 
    # doesn't really roll off the tongue
    print("Correlating events to suburban and rural boundaries...")
    rural_events_gdf = acled_gdf[acled_gdf.index_right.isnull()]
    rural_events_gdf = rural_events_gdf.dropna(axis='columns', how='all')
    rural_events_gdf = rural_events_gdf.sjoin(hromada_gdf, how="left")

    # Now discard all the rural events we couldn't match 
    urban_events_gdf = acled_gdf.dropna(axis='index', how='any') 

    urban_events_gdf = urban_events_gdf.drop(['index_right','ADM4_EN','ADM4_UA','ADM3_EN','ADM3_UA','ADM2_EN','ADM2_UA','ADM1_EN','ADM1_UA'], axis='columns')
    rural_events_gdf = rural_events_gdf.drop(['index_right','ADM3_EN','ADM3_UA','ADM2_EN','ADM2_UA','ADM1_EN','ADM1_UA'], axis='columns')

    # Now that the initial correlation is done, we'll jettison the point geometry in 
    # favor of the polygon geometry for the enclosing named territory
    urban_shapes_gdf = urban_gdf.copy()
    rural_shapes_gdf = hromada_gdf.copy()

    print(f"Joining urban and rural events to associated administrative boundaries...")
    urban_shapes_gdf = gpd.sjoin(urban_shapes_gdf, urban_events_gdf, how='inner', lsuffix='_hdx', rsuffix='_acled')
    rural_shapes_gdf = gpd.sjoin(rural_shapes_gdf, rural_events_gdf, how='inner', lsuffix='_hdx', rsuffix='_acled')

    assert(len(urban_shapes_gdf) == len(urban_events_gdf))
    assert(len(rural_shapes_gdf) == len(rural_events_gdf))

    urban_shapes_gdf['adm_name_en'] = urban_shapes_gdf['ADM4_EN']
    urban_shapes_gdf['adm_name_ua'] = urban_shapes_gdf['ADM4_UA']
    rural_shapes_gdf['adm_name_en'] = rural_shapes_gdf['ADM3_EN']
    rural_shapes_gdf['adm_name_ua'] = rural_shapes_gdf['ADM3_UA']

    print(f"Merging shapes back to a primary dataframe... ")
    events_gdf = pd.concat([urban_shapes_gdf, rural_shapes_gdf]) 
    assert(len(events_gdf) == len(acled_gdf))

    print(f"Dropping spatial join cruft... ")
    events_gdf.drop(
        [
            'ADM4_EN', 
            'ADM4_UA', 
            'ADM3_EN', 
            'ADM3_UA', 
            'ADM2_EN', 
            'ADM2_UA',
            'ADM1_EN', 
            'ADM1_UA', 
            'index__acled', 
        ], 
        axis='columns', 
        inplace=True
    )

    print(f"Spatial join on ACLED data complete.")

    return events_gdf

def get_rect_dims(rect): 
    """
    Calculation the height and width of parallelogram with sides running parallel to 
    the x and y axis. Returns tuple of (h, w)
    """
    xx,yy = rect.exterior.coords.xy
    h = xx[0] - xx[2]
    w = yy[0] - yy[2]
    return (h,w)

def make_firms_ukraine_pixel(scan, track, lat, long, angle=-90, km_per_dd_lat=111, km_per_dd_lng=75): 
    """
    Given the scan, track and centerpoint of a FIRMS detection, emit a polygon that 
    represents the geometry for someplace in Ukraine. The scan and track are used to
    offset increments of  decimal degrees to set the corners of the polygon, rotated
    by the provided angle. 

    This is a crude method, because 
    a) we presume using a single scaling factor to map scan/track distances 
    into coordinate changes (and in the case of longitude, that could be off
    by 5% or more depending on the latitude 
    b) we are not considering the effect of elevation.
    c) it is not clear from the documentation on the NASA imagers what the orientation 
    of the track direction is with respect to north. if it varies, it would presumably 
    materialize in the data feed. since it doesn't, we are presuming the 4-5 spacecraft
    which are carrying these imagers are tracking across the same roughly north/south 
    path... if we later figure out how to determine the track angle with respect to north, 
    adjust the angle here as needed on a per-spacecraft or per-pass basis. 

    Notes: 
    - we would need to implement at least a latitude-dependent distance calculator
    to remove the error. That said, for the Ukraine, and for our purposes, you 
    can accept the fixed default here which is close, or provide your own value. 
    See https://edwilliams.org/gccalc.htm for a useful tool if you're hand-jamming 
    the km_per_dd_lng parameter. 
    - all operations are done in a 2d cartesian coordinate system, angle 
    of zero is along the positive x axis, aka east
    - FIRMS scan/track values are (and must be) in units of kilometers
    """
    # Whip up our distance conversion constants
    dd_per_km_lat = 1/km_per_dd_lat
    dd_per_km_lng = 1/km_per_dd_lng
    
    # Create a unit parallelogram and scale/rotate to represent the pixel
    coords = [ (0.5,0.5),(0.5,-0.5),(-0.5,-0.5),(-0.5,0.5),(0.5,0.5) ]
    p = shapely.Polygon(coords) 
    p = shapely.affinity.scale(p, xfact=track, yfact=scan, origin='center') 
    assert(get_rect_dims(p) == (track, scan))
    p = shapely.affinity.rotate(p, angle, origin='center') 

    # Map the parallelogram into GPS coordinates
    p = shapely.affinity.scale(p, xfact=dd_per_km_lng, yfact=dd_per_km_lat, origin='center')
    p = shapely.affinity.translate(p, xoff=long, yoff=lat) 
    return p 

def build_firms_pixels(firms_gdf): 
    """
    Fabricate the polygons associated with the FIRMS detections aka pixels
    """
    
    print(f"Building FIRMS pixel geometry...")
    firms_gdf['PIXEL'] = firms_gdf.apply(
        lambda x: make_firms_ukraine_pixel(x['SCAN'], x['TRACK'], x['LATITUDE'], x['LONGITUDE']), 
        axis='columns')
    firms_gdf.set_geometry('PIXEL', inplace=True) 

    _ = firms_gdf.set_crs(4326, inplace=True) 
    firms_gdf.drop('geometry', axis='columns', inplace=True) 
    firms_gdf.rename(columns={'PIXEL':'geometry'}, inplace=True)
    
    firms_gdf.set_geometry('geometry', inplace=True)

def label_detections(firms_gdf, acled_gdf): 
    """
    Find all of our FIRMS detections that have associated battlefield events
    """
    firms_gdf.rename(columns={'ACQ_DATE':'obs_date'}, inplace=True)
    acled_gdf.rename(columns={'event_date':'obs_date'}, inplace=True)

    acled_gdf['admin_shape'] = acled_gdf['geometry']

    print(f"Intersecting event data with FIRMS thermal anomalies (positive class)...")
    firms_labeled = gpd.sjoin(
        firms_gdf, 
        acled_gdf,  
        how='inner', 
        lsuffix='firms', 
        rsuffix='acled',
        on_attribute='obs_date')
    
    quiescent_end = datetime.datetime(2022, 2, 1)
    print(f"Sampling from quiescent period (prior to {quiescent_end}) (negative class)...")
    quiescent_gdf = firms_gdf[firms_gdf.obs_date < quiescent_end].sample(n=len(firms_labeled))
    
    print(f"Joining classes ...")
    firms_labeled = pd.concat([firms_labeled, quiescent_gdf]) 
    firms_labeled.set_geometry('admin_shape', inplace=True) 

    print(f"Renaming columsn for sanity...")
    firms_labeled.rename(columns={
        'LATITUDE': 'f_lat',
        'LONGITUDE': 'f_lng', 
        'BRIGHTNESS': 'f_bright',
        'SCAN': 'f_scan', 
        'TRACK': 'f_track', 
        'obs_date': 'date',
        'ACQ_TIME': 'f_acqtime', 
        'SATELLITE': 'f_sat', 
        'INSTRUMENT': 'f_inst',  
        'CONFIDENCE': 'f_conf',
        'BRIGHT_T31': 'f_bright31', 
        'FRP': 'f_frp',
        'DAYNIGHT': 'f_daynight',  
        'ACQ_DATETIME': 'f_datetime',
        #'geometry': 'firms_pixel', # geopandas sometimes struggles with names other than 'geometry' for the active geometry, leave it alone
        'index_acled': 'a_index',
        'event_id_cnty': 'a_event_id', 
        'disorder_type': 'a_type',
        'event_type': 'a_event', 
        'sub_event_type': 'a_subevent',
        'location': 'a_location', 
        'latitude': 'a_lat', 
        'longitude': 'a_lng',
        'geo_precision': 'a_geoprec', 
        'adm_name_en': 'h_adm_en', 
        'adm_name_ua': 'h_adm_ua',
        'admin_shape' : 'h_adm_shape'
    }, inplace=True)

    print(f"Setting primary geometry to admin boundary (in in lieu of FIRMS pixel)...")
    firms_labeled.set_geometry('h_adm_shape', inplace=True) 

    return firms_labeled


def main(): 
    """ 
    Command-line entrypoint. Script accepts no args, just chugs through 
    the dataset build. 
    """
    urban_gdf, hromada_gdf, ukraine_gdf = load_administrative_shapes("ukr_admbnd_sspe_20240416_AB_GDB.gdb")
    firms_gdf = load_firms_data(ukraine_gdf)
    acled_gdf = load_acled_data('ACLED/2020-09-01-2024-09-24-Ukraine.csv')

    usage = get_memory_usage(urban_gdf) + \
            get_memory_usage(hromada_gdf) + \
            get_memory_usage(ukraine_gdf) + \
            get_memory_usage(firms_gdf) + \
            get_memory_usage(acled_gdf) 
    
    print(f"Datasets loaded, total memory usage is {usage}.")

    intersect_times(firms_gdf, acled_gdf)
    clean_administrative_data(urban_gdf, hromada_gdf, acled_gdf)    
    acled_gdf = contextualize_events(acled_gdf, urban_gdf, hromada_gdf)
    build_firms_pixels(firms_gdf)
    fud_gdf = label_detections(firms_gdf, acled_gdf)
    
    print(f"Flashpoints ukraine dataset created!") 

    
    
def test_firms_pixel(): 
    track = 0.7
    scan = 0.35
    p = make_firms_ukraine_pixel(scan, track, 0, 0, angle=0)     
    assert(get_rect_dims(p) == (track, scan))

if __name__ == '__main__': 
    main()
    