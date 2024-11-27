# Datasheet for Flashpoints Ukraine Dataset (FUD)

Questions from the [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) paper, v7.

Jump to section:
code
- [Motivation](#motivation)
- [Composition](#composition)
- [Collection process](#collection-process)
- [Preprocessing/cleaning/labeling](#preprocessingcleaninglabeling)
- [Uses](#uses)
- [Distribution](#distribution)
- [Maintenance](#maintenance)

## Motivation

### For what purpose was the dataset created? 

The Russo-Ukrainian war has had a devastating impact on the Ukrainian and Russian peoples alike. Estimates at the time of this writing put the total number of combatants killed or injured from both sides at almost half a million*. The tactical gains and strategic maneuvering of both sides is the subject of global interest, and significant geopolitical decisions turn on assessment of the war. The Flashpoint Ukraine Dataset (FUD) fuses authoritative data sources from the Armed Conflict Location & Event Data (ACLED), the Humanitarian Data Exchange, and NASA. The resulting composite view enables users to investigate whether there are latent patterns in NASA thermal anomaly data that enable prediction of conflict events. 

### Who created the dataset (e.g., which team, research group) and on behalf of which entity (e.g., company, institution, organization)?

Created by the author in support of graduate coursework at Duke University. 

### Who funded the creation of the dataset? 

The dataset creation was not funded. However, a significant and likely unpayable debt is owed to the caffeine molecule and its instances metabolized by the author during dataset development. 

## Composition

### What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?

The dataset consists of spatially anchored thermal anomalies in the obeervation period (see below), conditioned on conflict events.

The data can be employed in a variety of downstream analyses, however they are intended to power a binary classifier that achieves some success in inferring conflict events based on associated thermal anomalies.  

### How many instances are there in total (of each type, if appropriate)?

The data is comprised of 135,050 FIRMS-sourced anomalies. To support attempts at binary classification, a balance of positive and negative classes are provided as follows: 
  - 67525 positive class instances: here the anomaly is linked temporally and spatially with a coincident conflict event as reported by ACLED
  - 67525 negative class instances: the anomaly has no corresponding conflict event, and uniformly occurred during the relative quiescent period of 2020-2022 prior to the Russian invasion in February of 2022.

### Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?

The initial dataset includes all known FIRMS pixels reported for the window of study. Spatio-temporal correlation with conflict events reduces the initial population of well over 1 million pixels to ~67 thousand for the positive class (see above). The negative class is a random sample of pixels prior to conflict escalation in February of 2022. The sample count is driven exactly by the number of positive classes we arrive at through the aforementioned spatio-temporal join. 

### What data does each instance consist of? 

**FIRMS-Derived Columns**

FIRMS-derived columns in the dataset are prefixed with `f_`. For proper treatment of each, refer to the FIRMS [active fire data documentation](https://www.earthdata.nasa.gov/data/tools/firms). 

- `f_lat`: latitude of the center point of the thermal anomaly
- `f_lng`:  longitude of the center point of the thermal anomaly
- `f_bright`: brightness temperature of the anomaly
- `f_scan`: length of the pixel in km in the scan direction (~east/west orientation)
- `f_track`: length of the pixel in km in the track direction (~north/south orientation)
- `date`: date of the detection and the associated conflict event
- `f_acqtime`: pixel acquisition time
- `f_sat`: spacecraft carrying the observing instrument
- `f_inst`: instrument responsible for the observation
- `f_conf`: confidence of the obsevation (normalized across the dataset to low, medium, high)
- `f_bright31`: secondary wavelength brightness (see [FIRMS FAQ](https://www.earthdata.nasa.gov/data/tools/firms/faq)
- `f_frp`: pixel radiative power (see [FIRMS FAQ](https://www.earthdata.nasa.gov/data/tools/firms/faq)
- `f_daynight`: whether this is day or night observation
- `f_datetime`: datetime of the observation
- `geometry`: estimated pixel geometry

Note on pixels and geometry: FIRMS detections are rendered as pixels, each with a width and length indicated by the scan and track features. The orientation of the FIRMS fire pixels depends on the azimuth of spacecraft's earth track. Other than noting the spacecraft are all in a polar sun-synchronous orbit which would roughly result in a north/south orientation of the track direction. The dataset draws polygons that represents the FIRMS pixels prior to executing spacial joins. A heuristic is used to stretch these based on the expected deformation due to coverging longitude lines. This heuristic can result in up to ~5% error in the pixel geometry depending on the longitude of the pixel in question. A more rigorous spatial representation is certainly possible, but the technique feels rational given the aspirations of this dataset. 

Note on brightness: Per the [NASA FIRMS FAQ](https://www.earthdata.nasa.gov/data/tools/firms/faq):

> The brightness temperature of a fire pixel is measured (in Kelvin) using the MODIS channels 21/22 and channel 31. Brightness temperature is actually a measure of the photons at a particular wavelength received by the spacecraft, but presented in units of temperature.

Note on confidence: MODIS can report confidence as a percentage (0-99), while the other platforms consistently report confidence as low, medium or high. The decision was made to use equal intervals for the inconsistent MODIS confidences (L: 0-33,ML 34-66, H:67-99). This results in a consistent categories but introduces the potential for disparities in inference. Further research to properly map the confidence values wouldn't be a terrible idea. See also the [MODIS user guide](https://www.earthdata.nasa.gov/sites/default/files/imported/MODIS_C6_Fire_User_Guide_B.pdf).

**ACLED-Derived Columns**

ACLED-derived columns are prefixed with `a_` in the dataset. A thorough description of features of the ACLED data is provided in the [ACLED codebook](https://acleddata.com/knowledge-base/codebook/). See also the ACLED [Ukraine-specific coding methodology](https://acleddata.com/knowledge-base/acled-methodology-and-coding-decisions-around-conflict-in-ukraine/). 

- `a_event_id`: unique identifier that maps to the original ACLED event row
- `a_type`: the type of disorder motivating the event reporting
- `a_event`: the major category of event 
- `a_subevent`: the minor category of the event
- `a_location`: the English placename associated with the event
- `a_lat`: the latitude of the named location
- `a_lng`: the longitude of the named location
- `a_geoprec`: a categorical value indicating the resolution of the spatial correlation

It is helpful to appreciate the data collection and coding methodologies laid out in [the ACLED code book](https://acleddata.com/knowledge-base/codebook/). See also specific methodology applied to the Ukraine conflict in the [ACLED knowledge base](https://acleddata.com/knowledge-base/acled-methodology-and-coding-decisions-around-conflict-in-ukraine/). The decisions in attribution of events, grouping and disabiguation of combatants as well as fatality reporting may have bearing on downstream use of this aggregate dataset.

The nature of ACLED reporting implicitly creates an order of precdence for events and subevent types that may be important to understand for any downstream analysis. For exaample, ACLED favors “battles” events over individual attacks or strikes. The latter can be masked by the former accordingly. “When an ‘Explosions/Remote violence’ event is reported in the context of an ongoing battle, it is merged and recorded as a single ‘Battles’ event”. From the codebook: 

> rebel group fights with government forces in a town and wins control. Rebel artillery strikes are reported throughout the day. In this case, only a single ‘Battles’ event between the rebels and the government forces is recorded, instead of one ‘Battles’ event and another ‘Explosions/Remote violence’ event.

Note ACLED conflict events are reported at a daily resolution. Ongoing events are decomposed and spread over the days they affect. See the [codebook section](https://acleddata.com/knowledge-base/codebook/#event-time).

**HDX-Derived Columns**

Humanitarian Data Exchange (HDX) data are prefixed with `h_`.

- `h_adm_en`: administrative place name, transliterated into English
- `h_adm_ua`: administrative place name, in Ukrainian
- `h_adm_shape`: polygon(s) associated with the named administrative boundary

See also a list of Ukrainian [Hromadas](https://en.wikipedia.org/wiki/List_of_hromadas_of_Ukraine).

### Is there a label or target associated with each instance?

Positive labels are evidenced by the presence of an event and associated event metadata. Negativel labels are indicated by the absence of same. 

### Is any information missing from individual instances?

Negative classes are missing event features, this is intentional as the event IS the label (see above). 

### Are relationships between individual instances made explicit (e.g., users’ movie ratings, social network links)?

Relationships are implicit in the included spatial and temporal information, otherwise no relationships are intended beyond those that might be latent (and that we are interested in extracting). 

### Are there recommended data splits (e.g., training, development/validation, testing)?

Random sampling without replacement is recommended, no fractions are obvious at the time of initial publication. 

### Are there any errors, sources of noise, or redundancies in the dataset?

There are presumably copious opportunities for errors and noise to be introduced to tributary datasets, and these are called out where possible in this datasheet. The user is referred to the originators for more thorough treatment of these issues. For example, FIRMS data is reliant on VIIRS and MODIS sensors, usage and error characteristics are described [here](https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_User_Guide.pdf) and [here](https://www.earthdata.nasa.gov/sites/default/files/imported/MODIS_C6_Fire_User_Guide_B.pdf), respectively.

### Is the dataset self-contained, or does it link to or otherwise rely on external resources (e.g., websites, tweets, other datasets)?

The dataset as currently published is self contained. 

### Does the dataset contain data that might be considered confidential (e.g., data that is protected by legal privilege or by doctor-patient confidentiality, data that includes the content of individuals’ non-public communications)?

No

### Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?

No.

### Does the dataset relate to people? 

Indirectly, many correlated conflict events involve people. 

### Does the dataset identify any subpopulations (e.g., by age, gender)?

No .

### Is it possible to identify individuals (i.e., one or more natural persons), either directly or indirectly (i.e., in combination with other data) from the dataset?

No. 

### Does the dataset contain data that might be considered sensitive in any way (e.g., data that reveals racial or ethnic origins, sexual orientations, religious beliefs, political opinions or union memberships, or locations; financial or health data; biometric or genetic data; forms of government identification, such as social security numbers; criminal history)?

No.

### Any other comments?

None. 

## Collection process

### How was the data associated with each instance acquired?

The tributary datasets rely on: 
- remote sensing (orbiting spacecraft) 
- local, regional and national news and event reporting
- government-furnished (presumably) shapes of administrative regions (mostly Ukrainian Hromadas and cities)

### What mechanisms or procedures were used to collect the data (e.g., hardware apparatus or sensor, manual human curation, software program, software API)?

Refer to the tributary dataset collection protocols linked elsewhere. 

### If the dataset is a sample from a larger set, what was the sampling strategy (e.g., deterministic, probabilistic with specific sampling probabilities)?

Two classes are furnished. Positive classes where deterministically arrived at through a sequence of temporal and spatial joins on enriched and thresholded data. Negative classes were probabilistically sampled from thermal anomalies to create a balanced dataset. 

### Who was involved in the data collection process (e.g., students, crowdworkers, contractors) and how were they compensated (e.g., how much were crowdworkers paid)?

Dataset creation was an individual effort. For information regarding the tributary datasets, see the respective dataset websites.  

### Over what timeframe was the data collected?

The composite dataset contains events that were collected from 1 September 2020 through 24 September 2024. 

### Were any ethical review processes conducted (e.g., by an institutional review board)?

No

### Does the dataset relate to people?

A significant portion of the events used to label thermal anomalies are based on events involving people. No personally-identifiable information or information that disadvantages individuals is included in this dataset. All information relating to individuals are anonymized as outlined in the [ACLED sourcing methodology](https://acleddata.com/knowledge-base/faqs-acled-sourcing-methodology/). Furthermore, only ACLED categorical data has been incorporated into the synthesis that produced this dataset. 

### Did you collect the data from the individuals in question directly, or obtain it via third parties or other sources (e.g., websites)?

All information pertaining to persons was sourced through ACLED based on curation of availale reporting. See [ACLED sourcing methodology](https://acleddata.com/knowledge-base/faqs-acled-sourcing-methodology/).

### Were the individuals in question notified about the data collection?

Not applicable.

### Did the individuals in question consent to the collection and use of their data?

Not applicable.

### If consent was obtained, were the consenting individuals provided with a mechanism to revoke their consent in the future or for certain uses?

Not applicable. 

### Has an analysis of the potential impact of the dataset and its use on data subjects (e.g., a data protection impact analysis) been conducted?

No. However due to the aforementioned anonymization and strict controls on the tributary ACLED dataset, coupled with exclusive use of categorcal event data, the author believes there is minimal risk on the subjects of the included event reporting.

Not all future uses of the dataset can be anticipated, however the sincere belief of the curator is that the data offers potential to improve outcomes for humanitarian agencies, first-responders and democratic governments working to reduce violence in Ukraine. 

### Any other comments?

## Preprocessing/cleaning/labeling

### Was any preprocessing/cleaning/labeling of the data done (e.g., discretization or bucketing, tokenization, part-of-speech tagging, SIFT feature extraction, removal of instances, processing of missing values)?

The following excerpt from the dataset build script highlights the various transformations that occur between the ingest of the raw data to production of the final dataset. Note this build applies a 5% sample which is bypassed in the final dataset construction. 

```
Welcome to the flashpoint Ukraine dataset (FUD) builder!

Opening geodatabase ukr_admbnd_sspe_20240416_AB_GDB.gdb...
Enumerating layers...
 - 0 ukr_admbndt_adminUnitLookup
 - 1 ukr_admbndp_adm0123_sspe_itos_20240416
 - 2 ukr_admbndl_adm0123_sspe_itos_20240416
 - 3 ukr_admbnda_adm4_sspe_20240416
 - 4 ukr_admbnda_adm3_sspe_20240416
 - 5 ukr_admbnda_adm2_sspe_20240416
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

Datasets loaded.

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
Writing as shapefile...
Wrote export/shapefile/fud.shp et al.
Writing as geodatabase...
Wrote export/shapefile/fud.shp et al.

Thank you for choosing FUD.
```

### Was the “raw” data saved in addition to the preprocessed/cleaned/labeled data (e.g., to support unanticipated future uses)?

Yes. Details follow. While each of the datasets was preserved, license terms prevent raw data redistribution. Raw data should be requested from the source based on the below information. 

NASA-FIRMS : 

- Request URL: https://firms.modaps.eosdis.nasa.gov/download/
- Download Id(s): 519172 519173 519174 519175
- Data Source: modis-c6.1,jpss1-viirs-c2,jpss2-viirs-c2,suomi-viirs-c2
- Area of Interest: 18.4,39.6,49.1,57.5
- Date Range: 2020-09-01 to 2024-09-24
- Data Format: .shp 
- Request Time: 2024-09-24

Armed Conflict Location & Event Data (ACLED): 

- Request URL: https://acleddata.com/data-export-tool/
- Data Format: .csv
- Countries: Ukraine
- Date Range: 2022-01-01 to 2024-10-30
- Request Time: 2024-10-30

Humanitarian Data Exchange

- Download URL: https://data.humdata.org/dataset/cod-ab-ukr
- Data Format: .gdb
- Request Time: 2024-11-17

Spatial join and event attribution strategy: 
- We attribute reported conflict events to the smallest administrative division (city-level or failing that, Ukraianian Hromada) associated, as attested to in the ACLED documentation: 
  > Locations are recorded to named populated places, geostrategic locations, natural locations, or neighborhoods of larger cities. Geo-coordinates with four decimals are provided to assist in identifying and mapping named locations to a central point (i.e. a centroid coordinate) within that location. Geo-coordinates do not reflect a more precise location, like a block or street corner, within the named location.
- So theremal anomalies occurring within the confines of the Avdiivka hromada, where conflict events concurrently took place, are joined and labeled.

### Is the software used to preprocess/clean/label the instances available?

Yes. See [here](./build.py) and the more elaborate but perpelexing [research notebook](./fud.ipynb).

### Any other comments?

On interpretation of ACLED events, and our subsetting to arrive at the events with some plausible chance to induce a thermal anomaly: 
- The Battles and Explosions/Remote violence are the most relevant event types, but the disruption of attacks (notably by shooting down UAVs/drones and other ordance is retained based on its obvious potential to mirror conflict activity and induce thermal anomalies
- See [ACLED event types article](https://acleddata.com/2019/03/14/acled-introduces-new-event-types-and-sub-event-types/) for more information on 'disrupted weapons use' which seems quite relevant (e.g. UAV intercept).

On the topic of suitably quantifying the underlying phenomena, and the limitations of our aperture into real events: 
- A thermal anomaly motivated by conflict could have occurred, with no ACLED reporting to match
- Seasonal or non-conflict fires will be represented in this data, but because we cannot disambiguate from those induced by conflict events without event data, we cannot apply a label
- The event could have occurred as advertised in the ACLED data, but no thermal data.
- The event could have occurred, and generated a thermal anomaly but not been collected due to overflight timing or weather, or because the fire was too small to be detected, or because there was no fire at all! 

On the topic of labeling: 
- ACLED events with no thermal correlation are a sort of negative class, but it's not a false negative per se, at least because of the overflight and the sensor sensitivity problems. 
- We have to have true negatives, our only option here due to the confounded of weather is to incorporate all thermal anomalies before the escalation in 2022 and assert that effectively zero of those thermal anomalies were the result of conflict events. 
- For all of the above reasons, we crutch on thermal anomalies that occurred prior to the most recent stage of this conflict when Russia invaded Ukraine. While we introduce more confounders like annual fluctuations in temperature or fire, it seems the best of the options in front of us. 

## Uses

As described elsewhere in this datasheet, the data is intended to support exploration of the potentially reproducible correlations between NASA-reported thermal anomalies and Ukrainian conflict events. An optimal outcome would be for binary classifier to be trained of some reasonable accuracy which infers events based on near-real-time NASA FIRMS feeds. This would conceivably augment the efforts of humanitarian agencies, first-responders and democratic governments, cuing responses or more in-depth reporting. 

### Has the dataset been used for any tasks already?

Work in progress. 

### Is there a repository that links to any or all papers or systems that use the dataset?

No. 

### What (other) tasks could the dataset be used for?

### Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?

Relevant information in other sections of this datasheet. 

### Are there tasks for which the dataset should not be used?

The lack of rigorous quality controls and analysis of methods by persons knowledgable in remote sensing, conflict journalism, geographic information systems, and statistics suggests caution proportionate to the seriousness of the application.

### Any other comments?

## Distribution

### Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created? 

Unknown. 

### How will the dataset will be distributed (e.g., tarball on website, API, GitHub)?

Kaggle.com as both shapefile and geopackage. 

### When will the dataset be distributed?

From 26 November 2024. 

### Will the dataset be distributed under a copyright or other intellectual property (IP) license, and/or under applicable terms of use (ToU)?

Yes. [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). 

### Have any third parties imposed IP-based or other restrictions on the data associated with the instances?

NASA FIRMS data is open and shareable. 

Humanitarian Data Exchange data is open and shareable under the Creative Commons Attribution for Intergovernmental Organisatiosn (CC BY-IGO). See [HDX licenses](https://data.humdata.org/faqs/licenses).

> Under the CC BY-IGO license, you are free to share (copy and redistribute the material in any medium or format) and or adapt (remix, transform, and build upon the material) for any purpose, even commercially. The licensor cannot revoke these freedoms as long as you follow the license terms. The license terms are that you must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. Additionally, you may not apply legal terms or technological measures that legally restrict others from doing anything the license permits. When the Licensor is an intergovernmental organization, disputes will be resolved by mediation and arbitration unless otherwise agreed.

### Do any export controls or other regulatory restrictions apply to the dataset or to individual instances?

As the research is made freely available and qualifies as fundamental research, it is exempted from the International Trade in Arms Regulation (ITAR) and US Department of Commerce export rules. 

### Any other comments?

## Maintenance

### Who is supporting/hosting/maintaining the dataset?

The author. Maybe. 

### How can the owner/curator/manager of the dataset be contacted (e.g., email address)?

jason.mooberry@duke.edu

### Is there an erratum?

Not at the time of this initial releease. 

### Will the dataset be updated (e.g., to correct labeling errors, add new instances, delete instances)?

Demand dependent. 

### If the dataset relates to people, are there applicable limits on the retention of the data associated with the instances (e.g., were individuals in question told that their data would be retained for a fixed period of time and then deleted)?

NA/

### Will older versions of the dataset continue to be supported/hosted/maintained?

No. 

### If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?

Yes. The most obvious and welcome path is collaboration via the Github project (which you might be reading this datasheet on): https://github.com/auto-d/ukraine_analysis

### Any other comments?

None. 


