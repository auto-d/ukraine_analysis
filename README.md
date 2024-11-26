# Flashpoint Ukraine Dataset (FUD)

## Motivation 

The Russo-Ukrainian war has had a devastating impact on the Ukrainian and Russian peoples alike. Estimates at the time of this writing put the total number of combatants killed or injured from both sides at almost half a million†. The tactical gains and strategic maneuvering of both sides is the subject of global interest, and significant geopolitical decisions turn on assessment of the war. Concurrently a multitude of humanitarian groups and indigenous agencies rely on event reporting to improve conditions for affected populations. Anecdotal evidence suggests that NASA-sourced thermal anomaly data is correlated with conflict events. The Flashpoint Ukraine Dataset (FUD) fuses authoritative data sources‡ and delivers a composite geospatially correlated dataset to explore this relationship.

† New York Times. (2024, September 24). Troop deaths and injuries in Ukraine war near 500,000, U.S. officials say. https://www.nytimes.com

‡ Tributary datasets from the Armed Conflict Location & Event Data (ACLED), the UN Office for the Coordination of Humanitarian Affairs - Field Information Services Section, and NASA Fire Information for Resource Management System (FIRMS). 

## Prior Work and Differentiation 

Anecdotal evidence and visual inspection of manual analysis seem to suggest a correlation between thermal anomalies and conflict activity in the Ukraine. To the author's knowledge, no dataset that attempts to integrate hyperspectral thermal anomalies and conflict events through spatial analysis has been made public.

## Datasheet

In an effort to improve the clarity with which the dataset is presented as well as its utility to users, [a datasheet](./datasheet.md) is furnished in the style outlined by Gebru, et al in [1]. The authors assert the following about the rationale: 
> Datasheets for datasets are intended to address the needs of two key stakeholder groups: dataset creators and dataset consumers. For dataset creators, the primary objective is to encourage careful reflection on the process of creating, distributing, and maintaining a dataset, including any underlying assumptions, potential risks or harms, and implications of use. For dataset consumers, the primary objective is to ensure they have the information they need to make informed decisions about using a dataset. 

Provenance, uses, licensing, and a host of standard questions surrounding dataset distribution can be found in the datasheet. 

[1] Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Iii, H. D., & Crawford, K. (2021). Datasheets for datasets. Communications of the ACM, 64(12), 86-92.

## Sourcing

Tributary datasets are outlined in the associated datasheet. Briefly: 
- Administrative shapes provided by UN Office for the Coordination of Humanitarian Affairs - Field Information Services Section, uploaded to Humanitarian Data Exchange (HDX) and released under [Creative Commons Attribution for Intergovernmental Organizations](https://data.humdata.org/faqs/licenses). 
- Thermal anomaly detections sourced by National Aeronautics and Space Administration (NASA) Fire Information for Resource Management System (FIRMS), released under free and open policy for data sharing. See [here](https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-policy).
- Ukraine conflict events sourced by [Armed Conflict Location & Event Data (ACLED)](www.acleddata.com.), and [made available for academic research but not freely redistributable](https://acleddata.com/terms-of-use/). 

The [concurrently distributed albeit embarassingly unmanicured Jupyter notebook](./fud.ipynb) details the exploration, subsequent manipulation, and enrichment of the tributary datasets. 

### Tooling 

A repeatably methodology for dataset generation is provided in the [FUD build script](./build.py). 

## Power Analysis 

- ❗️ Review the framing of spatial statistics provided here:  https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-statistics/what-is-a-z-score-what-is-a-p-value.htm
    - Employ the ramdomization null hypothesis to help validate what we're seeing here with the nasa data
    - Note this might actually belong in our readme

- Frame this as a validation of the tributary datasets to gain confidence in their sourcing and conclude (hoepfully) that they are not the product of some random process (e.g. failure in the space platform sensor, etc..)
    - The move here might be to run the spatial null-hypothesis test for each of the tributary datasets, in a loop, to determine the degree to which their values deviate from a random sample
    - ACLED
    - modis: acqua, terra
    - viirs: whatever it's flying on (three spacecraft?)
- statistical power is a measure of how likely we are to be able to accept the alternative hypothesis in the face of random variations
    - this drives the sample size of our study. here we are only looking at the ukraine to try and infer the relationship between thermal anomalies and conflict events -- how does this pertain to the type of analysis statistic power is usually applied to?
        - ❗️well, if we are subsampling in our dataset, we could say something like "we have 1000000 events, but studying these at the macro level is cost prohibitive, the minimal number of events we need to infer a relationship between these two things (thermal anomalies and conflict) is 1000 based on the <insert basis rationale>. consequently we're going to conduct our analysis with a randomly sampled 1000 events.
            - ❗️hmm... but the ACLED and NASA data is itself a subset of the actual events that occurred, so subsetting this subset would result in our math being wrong. even presuning there are doulbe or tenfold increase in actual events could be an underrepresentation!
    - but what if our sample size is equal to the number of things we're studying? as pointed about above, we're not dealing with statistics anymore we're dealing with a collection of facts. in this case, we might be more interested in validating the observations are distinct from random fluctuations

## Exploratory Data Analysis 

The accompanying [exploratory data analysis notebook](./eda.ipynb) and it's companion [tributary dataset EDA notebook](./fud.ipynb) provide insights into the data and suggest options for future work.  

## Ethics

Covered in the enclosed [datasheet](./datasheet.md).

## Dataset Access

The associated dataset is [freely available on Kaggle](https://www.kaggle.com/datasets/justanotherjason/flashpoint-ukraine-dataset)

## Dataset License

The dataset is licensed under [Creative Commons Non-Commercial Sharealike 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Commercial use is prohibited consistent with ACLED data use agreements to support academic research and support to NGO humanitarian efforts. 

## Data Included

Exhaustively explained in the attached [datasheet](./datasheet.md). 

## Assembling 

Steps to assemble and organize dependent datasets are contained in the following three sections.

### Humanitarian Data Exchange Ukraine Administrative Boundaries

These shapes are central to the spatial joins that are the core of the thermal anomaly correlation. 

1. Download the Humanitarian Data Exchange Ukraine administrative boundaries, sourced by the UN: 
    - Download URL: https://data.humdata.org/dataset/cod-ab-ukr
    - Data Format: .gdb
2. Save .gdb into ./HDX/ and modify the script to accept the filename if different from the default of `ukr_admbnd_sspe_20240416_AB_GDB.gdb"`
 
### ACLED Ukraine 

1. Create a developer account at the ACLED Access Portal: https://developer.acleddata.com/
2. Once Access Key is received, request data that covers the window of interest: 
    - Request URL: https://acleddata.com/data-export-tool/
    - Data Format: .csv
    - Countries: Ukraine
    - Date Range: 2020-09-01 to 2024-09-24
3. Save the CSV into ./ACLED/ and modify script to accept if different than the default of `ACLED/2020-09-01-2024-09-24-Ukraine.csv`
     
### NASA-FIRMS : 

1. FIRMS data can be retrieved from the FIRMS portal. 
    - Request URL: https://firms.modaps.eosdis.nasa.gov/download/
    - Download Id(s): 519172 519173 519174 519175
    - Data Source: modis-c6.1,jpss1-viirs-c2,jpss2-viirs-c2,suomi-viirs-c2
    - Area of Interest: 18.4,39.6,49.1,57.5
    - Date Range: 2020-09-01 to 2024-09-24
    - Data Format: .shp 
2. Wait for your download link
3. Retrieve FIRMS archives and store into respect directories under /NASA-FIRMS. Note the unique download request identifier (e.g. 519173). 
    - NASA-FIRMS/DL_FIRE_J1V-C2_519173/fire_nrt_J1V-C2_519173.shp
    - NASA-FIRMS/DL_FIRE_J2V-C2_519174/fire_nrt_J2V-C2_519174.shp
    - NASA-FIRMS/DL_FIRE_SV-C2_519175/fire_archive_SV-C2_519175.shp
    - NASA-FIRMS/DL_FIRE_M-C61_519172/fire_archive_M-C61_519172.shp
4. Modify the build script to point to the downloaded files (update unique identifiers)

## Build

The build script expects the directory structure to exist as outlined above. That is, 

```
./
ACLED/ 
HDX/
NASA-FIRMS/
README.md
build.py
```

Running the build...

```
% python build.py 
Welcome to the flashpoint Ukraine dataset (FUD) builder!

Opening geodatabase ukr_admbnd_sspe_20240416_AB_GDB.gdb...
Enumerating layers...
 - 0 ukr_admbndt_adminUnitLookup
 - 1 ukr_admbndp_adm0123_sspe_itos_20240416
 - 2 ukr_admbndl_adm0123_sspe_itos_20240416
 - 3 ukr_admbnda_adm4_sspe_20240416
 - 4 ukr_admbnda_adm3_sspe_20240416
 - 5 ukr_admbnda_adm2_sspe_20240416
RuntimeWarning: organizePolygons() received a polygon with more than 100 parts. The processing may be really slow.  You can skip the processing by setting METHOD=SKIP, or only make it analyze counter-clock wise parts by setting METHOD=ONLY_CCW if you can assume that the outline of holes is counter-clock wise defined
  return ogr_read(
 - 6 ukr_admbnda_adm1_sspe_20240416
 - 7 ukr_admbnda_adm0_sspe_20240416
Loading urban shape data from layer 3
  Found 29707 polygons.
Loading hromada shape data from layer 4
  Found 1769 polygons.
Loading Ukraine shape data from layer 7
  Found 1 polygons.
Loaded adminstrative shapes.

Opening FIRMS data...
Reading data for j1v from NASA-FIRMS/DL_FIRE_J1V-C2_519173/fire_nrt_J1V-C2_519173.shp...
  Found 875035 records.
Reading data for j2v from NASA-FIRMS/DL_FIRE_J2V-C2_519174/fire_nrt_J2V-C2_519174.shp...
  Found 204292 records.
Reading data for sv from NASA-FIRMS/DL_FIRE_SV-C2_519175/fire_archive_SV-C2_519175.shp...
  Found 664824 records.
Reading data for modis from NASA-FIRMS/DL_FIRE_M-C61_519172/fire_archive_M-C61_519172.shp...
  Found 182469 records.
Cleaning fire classifications...
Cleaning version...
Homogenizing detection confidences...
Merging data...
 - adding j1v records
 - adding j2v records
 - adding sv records
 - adding modis records
Sampling data @ 5.0%
Creating datetime field...
Intersecting detections with provided geometry (1)...
Removing unneeded administrative boundary information... 
Loaded FIRMS data.

Loading ACLED data from ACLED/2020-09-01-2024-09-24-Ukraine.csv...
  Found 144700 records.
Converting event dates...
Removing events outside Ukraine...
Sampling data @ 5.0%
Pruning columns... 
Removing low temporal precision events...
Removing non-kinetic events...
  dropping Abduction/forced disappearance
  dropping Agreement
  dropping Peaceful protest
  dropping Other
  dropping Change to group/activity
  dropping Abduction/forced disappearance
  dropping Government regains territory
  dropping Suicide bomb
  dropping Excessive force against protesters
  dropping Violent demonstration
Creating geodataframe...
Droppping NaN rows...
Loaded ACLED data.

Cleaning unused columns from urban shapes...
Cleaning unused columns from Hromada shapes...
Cleaning unused columns from ACLED shapes...

Correlating events to city-level boundaries...
Correlating events to suburban and rural boundaries...
Joining urban and rural events to associated administrative boundaries...
Merging shapes back to a primary dataframe... 
Dropping spatial join cruft... 
Spatial join on ACLED data complete.

Building FIRMS pixel geometry...

Intersecting event data with FIRMS thermal anomalies (positive class)...
Sampling from quiescent period (prior to 2022-02-01 00:00:00) (negative class)...
Joining classes ...
Renaming columsn for sanity...
Setting primary geometry to admin boundary (in in lieu of FIRMS pixel)...

Flashpoints ukraine dataset created!

Writing as shapefile... (warnings are okay here)
UserWarning: Column names longer than 10 characters will be truncated when saved to ESRI Shapefile.
  one_shape.to_file(shp_file)
RuntimeWarning: Field date create as date field, though DateTime requested.
  ogr_write(
RuntimeWarning: Field f_datetime create as date field, though DateTime requested.
  ogr_write(
Wrote export/shapefile/fud.shp et al.
Writing as geodatabase... (warnings are okay here)
UserWarning: Column names longer than 10 characters will be truncated when saved to ESRI Shapefile.
  one_shape.to_file(shp_file)
RuntimeWarning: Field date create as date field, though DateTime requested.
  ogr_write(
RuntimeWarning: Field f_datetime create as date field, though DateTime requested.
  ogr_write(
Wrote export/shapefile/fud.shp et al.

Thank you for choosing FUD.
```

## Artifacts 

If everything went according to plan, the script writes the FUD as both a shapefile and a geopackage into the ./export subdirectory: 

```
% ls -R export
geopackage	shapefile

export/geopackage:
fud.gpkg

export/shapefile:
fud.cpg	fud.dbf	fud.prj	fud.shp	fud.shx
```
