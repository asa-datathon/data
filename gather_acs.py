#!/usr/bin/env python
#
# Script to pull down ACS data for the ASA Datathon
# Pulls 5-year estimate data from 2006-2010 ACS
#  
# References: 
# ACS handbook
# http://www.census.gov/acs/www/Downloads/handbooks/ACSGeneralHandbook.pdf
#
# 2006-2010 ACS variables
# http://api.census.gov/data/2010/acs5/variables.html

#
# By Alex Hanna <alex.hanna@gmail.com> 2014
# with much code borrowed from Pete Warden <pete@petewarden.com> 
# Released under the MIT License

import sys, time
from us import states
from census import Census 

CENSUS_API_KEY="0108a125f5c746e49dfd2fac2af43b5339e0c16b"

WANTED_MSAS = {
  'New York-Newark': [
    ['36', '027'],
    ['36', '079'],
    ['36', '059'],
    ['36', '103'],
    ['34', '013'],
    ['34', '019'],
    ['34', '027'],
    ['34', '035'],
    ['34', '037'],
    ['34', '039'],
    ['42', '103'],
    ['34', '003'],
    ['34', '017'],
    ['34', '023'],
    ['34', '025'],
    ['34', '029'],
    ['34', '031'],
    ['36', '005'],
    ['36', '047'],
    ['36', '061'],
    ['36', '071'],
    ['36', '081'],
    ['36', '085'],
    ['36', '087'],
    ['36', '119'],
  ],
  'Los Angeles-Long Beach-Anaheim': [
    ['06', '059'],
    ['06', '037'],
  ],
  'Chicago-Naperville-Elgin': [
    ['17', '031'],
    ['17', '043'],
    ['17', '063'],
    ['17', '093'],
    ['17', '111'],
    ['17', '197'],
    ['17', '037'],
    ['17', '089'],
    ['18', '073'],
    ['18', '089'],
    ['18', '111'],
    ['18', '127'],
    ['17', '097'],
    ['55', '059'],
  ],
  'Dallas-Fort Worth': [
    ['48', '085'],
    ['48', '113'],
    ['48', '121'],
    ['48', '139'],
    ['48', '231'],
    ['48', '257'],
    ['48', '397'],
    ['48', '221'],
    ['48', '251'],
    ['48', '367'],
    ['48', '425'],
    ['48', '439'],
    ['48', '497'],
  ],
  'Houston-The Woodlands-Sugarland': [
    ['48', '015'],
    ['48', '039'],
    ['48', '071'],
    ['48', '157'],
    ['48', '167'],
    ['48', '201'],
    ['48', '291'],
    ['48', '339'],
    ['48', '473'],
  ],
  'Philadelphia-Reading-Camden': [
    ['34', '005'],
    ['34', '007'],
    ['34', '015'],
    ['42', '017'],
    ['42', '029'],
    ['42', '091'],
    ['42', '045'],
    ['42', '101'],
    ['10', '003'],
    ['24', '015'],
    ['34', '033'],
  ],
  'Washington-Baltimore-Arlington': [
    ['24', '021'],
    ['24', '031'],
    ['11', '001'],
    ['24', '009'],
    ['24', '017'],
    ['24', '033'],
    ['51', '013'],
    ['51', '043'],
    ['51', '047'],
    ['51', '059'],
    ['51', '061'],
    ['51', '107'],
    ['51', '153'],
    ['51', '157'],
    ['51', '177'],
    ['51', '179'],
    ['51', '187'],
    ['51', '510'],
    ['51', '600'],
    ['51', '610'],
    ['51', '630'],
    ['51', '683'],
    ['51', '685'],
    ['54', '037'],
  ],
  'Miami-Fort Lauderdale-West Palm Beach': [
    ['12', '011'],
    ['12', '086'],
    ['12', '099'],
  ],
  'Atlanta-Athens-Clark County-Sandy Springs': [
    ['13', '059'],
    ['13', '195'],
    ['13', '219'],
    ['13', '221'],
    ['13', '013'],
    ['13', '015'],
    ['13', '035'],
    ['13', '045'],
    ['13', '057'],
    ['13', '063'],
    ['13', '067'],
    ['13', '077'],
    ['13', '085'],
    ['13', '089'],
    ['13', '097'],
    ['13', '113'],
    ['13', '117'],
    ['13', '121'],
    ['13', '135'],
    ['13', '143'],
    ['13', '149'],
    ['13', '151'],
    ['13', '159'],
    ['13', '171'],
    ['13', '199'],
    ['13', '211'],
    ['13', '217'],
    ['13', '223'],
    ['13', '227'],
    ['13', '231'],
    ['13', '247'],
    ['13', '255'],
    ['13', '297'],
  ],
  'Boston-Cambridge-Newton': [
    ['25', '021'],
    ['25', '023'],
    ['25', '025'],
    ['25', '009'],
    ['25', '017'],
    ['33', '015'],
    ['33', '017'],
  ],
  'San Francisco-Oakland-Hayward': [
    ['06', '001'],
    ['06', '013'],
    ['06', '075'],
    ['06', '081'],
    ['06', '041'],
  ],
}

# These files are tab-separated lists of tract IDs and their rough centroids as lat/lon pairs
COORDS_FILENAMES = [
  'tract_coords_2010.txt'
]

## Possible variables
## B11001.  Household Type (including Living Alone)
## B19001.  Household Income
## B19051.  Earnings for Households
## B19052.  Wage or Salary Income for Households
## B19053.  Self-Employment Income for Households
## B19054.  Interest, Dividends, or Net Rental Income for Households
## B19055.  Social Security Income for Households
## B19056.  Supplemental Security Income (SSI) for Households
## B19057.  Public Assistance Income for Households
## B19058.  Public Assistance Income or Food Stamps/SNAP in the Past 12 Months for Households
## B19059.  Retirement Income for Households
## B19301.  Per Capita Income
## B25002.  Occupancy Status
## B25003.  Tenure
## B25017.  Rooms
## B25018.  Median Number of Rooms
## B25063.  Gross Rent
## B25085.  PRICE ASKED

WANTED_CODES = [
	['Family Households', 'B11001_002E'],
  ['Nonfamily Households', 'B11001_007E'],
  ['Household income: < 10k', 'B19001_002E'],
  ['Household income: 10-15k', 'B19001_003E'],
  ['Household income: 15-20k', 'B19001_004E'],
  ['Household income: 20-25k', 'B19001_005E'],
  ['Household income: 25-30k', 'B19001_006E'],
  ['Household income: 30-35k', 'B19001_007E'],
  ['Household income: 35-40k', 'B19001_008E'],
  ['Household income: 40-45k', 'B19001_009E'],
  ['Household income: 45-50k', 'B19001_010E'],
  ['Household income: 50-60k', 'B19001_011E'],
  ['Household income: 60-75k', 'B19001_012E'],
  ['Household income: 75-100k', 'B19001_013E'],
  ['Household income: 100-125k', 'B19001_014E'],
  ['Household income: 125-150k', 'B19001_015E'],
  ['Household income: 150-200k', 'B19001_016E'],
  ['Household income: > 200k', 'B19001_017E'],
  ['With wage or salary income', 'B19052_002E'],
  ['No wage or salary income', 'B19052_003E'],
  ['With self-employment income', 'B19053_002E'],  
  ['No self-employment income', 'B19053_003E'],
  ['With interest dividends or net rental income', 'B19054_002E'],
  ['No interest dividends or net rental income', 'B19054_003E'],
  ['With Social Security income', 'B19055_002E'],
  ['No Social Security income', 'B19055_003E'],
  ['With Supplemental Security Income (SSI)', 'B19056_002E'],
  ['No Supplemental Security Income (SSI)', 'B19056_003E'],
  ['With public assistance income', 'B19057_002E'],
  ['No public assistance income', 'B19057_003E'],
  ['With cash public assistance or Food Stamps/SNAP', 'B19058_002E'],
  ['No cash public assistance or Food Stamps/SNAP', 'B19058_003E'],
  ['With retirement income', 'B19059_002E'],
  ['No retirement income', 'B19059_003E'],
  ['Per capita income (2010 dollars)', 'B19301_001E'],
  ['Housing units', 'B25001_001E'],
  ['Occupancy status: Occupied', 'B25002_002E'],
  ['Occupancy status: Vacant', 'B25002_002E'],
  ['Housing tenure: Owner-occupied', 'B25003_002E'],  
  ['Housing tenure: Renter-occupied', 'B25003_003E'],
  ['Median number of rooms', 'B25018_001E'],
  ['Median gross rent (dollars)', 'B25064_001E'],
  ['Median value for owner-occupied housing', 'B25077_001E']
]

coords_by_geoid = {}
for coord_filename in COORDS_FILENAMES:
  sys.stderr.write("Loading coordinates from %s\n" % coord_filename)
  with open(coord_filename) as file:
    for line in file:
      parts = line.strip().split("\t")
      if len(parts) != 3:
        continue
      geo_id, lat, lon = parts
      coords_by_geoid[geo_id] = [lat, lon]

c = Census(CENSUS_API_KEY)

## writing headers
headers = ['MSA','Tract ID', 'Latitude', 'Longitude']
for code_info in WANTED_CODES:
  label = code_info[0]
  headers.append(label)
print ','.join(headers)

for msa_name, counties_for_msa in WANTED_MSAS.items():
  sys.stderr.write("Working on %s\n" % msa_name)
  for state_and_county in counties_for_msa:
    state_fips = state_and_county[0]
    county_fips = state_and_county[1]
    statistics_by_tract = {}
    for code_info in WANTED_CODES:
      label = code_info[0]
      code  = code_info[1]
      
      statistics_for_code = []
      for attempt in range(3):
        statistics_for_code = c.acs.state_county_tract(code, state_fips, county_fips, Census.ALL, year = 2010)
        if len(statistics_for_code) == 0:
          sys.stderr.write("Bad result for code '%s' for state %s and county %s in year %d\n" % (code, state_fips, county_fips, 2010))
          time.sleep(1.0)
          continue
        break
      if len(statistics_for_code) == 0:
        sys.stderr.write("All retries failed\n")
        raise Exception("Bad API result")
      for row in statistics_for_code:
        tract_id = row['tract']
        if len(tract_id) == 5:
          tract_id = '0' + tract_id
        elif len(tract_id) == 4:
          tract_id = tract_id + '00'
        elif len(tract_id) == 3:
          tract_id = tract_id + '000'
        geo_id = state_fips + county_fips + tract_id
        if geo_id not in statistics_by_tract:
          statistics_by_tract[geo_id] = {'msa_name': msa_name}
        key = label
        statistics_by_tract[geo_id][key] = row[code]

    for geo_id, tract_statistics in statistics_by_tract.items():
      msa_name = tract_statistics['msa_name']
      if geo_id in coords_by_geoid:
        lat, lon = coords_by_geoid[geo_id]
      else:
        lat = ''
        lon = ''
      values = [msa_name, geo_id, str(lat), str(lon)]
      for code_info in WANTED_CODES:
        label = code_info[0]
        code  = code_info[1]
  
        key = label
        if key in tract_statistics:
          value = tract_statistics[key]
        else:
          value = ''
        values.append(value)
      
      print ','.join(map( lambda x: '' if not x else x, values )) 

