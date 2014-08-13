#!/usr/bin/env python
#
# Script to pull down US Census data for the ASA Hackathon
# By Pete Warden <pete@petewarden.com> 2014
# Released under the MIT License

from us import states
from census import Census
import sys
import time

# You'll need to get your own key at http://www.census.gov/developers/
CENSUS_API_KEY='b4e8add27414d5f6165ff485a6503b168cdf0c59'

# Each row of this table is <readable label>, <2010 code>, <2000 code>, <1990 code>
WANTED_CODES = [
  ['Population', 'P0030001', 'P003001', 'P0030001'],
  ['White', 'P0030002', 'P003002', 'P0060001'],
  ['Black or African American', 'P0030003', 'P003003', 'P0060002'],
  ['American Indian and Alaska Native', 'P0030004', 'P003004', 'P0060003'],
  ['Asian', 'P0030005', 'P003005', 'P0060004'],
  ['Native Hawaiian and Other Pacific Islander', 'P0030006', 'P003006', ''],
  ['Other Race', 'P0030007', 'P003007', 'P0060005'],
  ['Two or More Races', 'P0030008', 'P003008', ''],
  ['Not Hispanic or Latino', 'P0040002', 'P004002', ''],
  ['Hispanic or Latino', 'P0040003', 'P004003', 'P0080001'],
  ['Male', 'P0120002', 'P012002', 'P0050001'],
  ['Female', 'P0120026', 'P012026', 'P0050002'],
  ['Median Age', 'P0130001', 'P013001', ''],
  ['Households', 'P0180001', 'P018001', 'P0030001'],
  ['Family Households', 'P0180002', 'P018002', 'P0260001'],
  ['Husband-wife family', 'P0180003', 'P018003', 'P0180001'],
  ['Male no wife present', 'P0180005', 'P018005', 'P0180002'],
  ['Female no husband present', 'P0180006', 'P018006', 'P0180003'],
  ['Living alone', 'P0180008', 'P018008', ''],
  ['Living with roommates', 'P0180008', 'P018008', ''],
  ['Households with over-60\'s', 'P0240002', 'P024002', ''],
]
WANTED_YEARS = [2010, 2000, 1990]
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

c = Census(CENSUS_API_KEY)

headers = ['MSA','Tract ID']
for code_info in WANTED_CODES:
  label = code_info[0]
  for index, year in enumerate(WANTED_YEARS):
    code = code_info[index + 1]
    if code == '':
      continue
    key = label + ' ' + str(year)
    headers.append(key)
print ','.join(headers)

for msa_name, counties_for_msa in WANTED_MSAS.items():
  sys.stderr.write("Working on %s\n" % msa_name)
  for state_and_county in counties_for_msa:
    state_fips = state_and_county[0]
    county_fips = state_and_county[1]
    statistics_by_tract = {}
    for code_info in WANTED_CODES:
      label = code_info[0]
      for index, year in enumerate(WANTED_YEARS):
        code = code_info[index + 1]
        if code == '':
          continue
        # Fix up for change to Miami/Dade County FIPS code between 1990 and 2000
        if state_fips == '12' and county_fips == '086' and year == 1990:
          api_county_fips = '025'
        else:
          api_county_fips = county_fips
        statistics_for_code = []
        for attempt in range(3):
          statistics_for_code = c.sf1.state_county_tract(code, state_fips, api_county_fips, Census.ALL, year=year)
          if len(statistics_for_code) == 0:
            sys.stderr.write("Bad result for code '%s' for state %s and county %s in year %d\n" % (code, state_fips, api_county_fips, year))
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
          if len(tract_id) == 4:
            tract_id = tract_id + '00'
          row_id = state_fips + county_fips + '_' + tract_id
          if row_id not in statistics_by_tract:
            statistics_by_tract[row_id] = {'msa_name': msa_name}
          key = label + ' ' + str(year)
          statistics_by_tract[row_id][key] = row[code]

    for tract_id, tract_statistics in statistics_by_tract.items():
      msa_name = tract_statistics['msa_name']
      values = [msa_name, tract_id]
      for code_info in WANTED_CODES:
        label = code_info[0]
        for index, year in enumerate(WANTED_YEARS):
          code = code_info[index + 1]
          if code == '':
            continue
          key = label + ' ' + str(year)
          if key in tract_statistics:
            value = tract_statistics[key]
          else:
            value = ''
          values.append(value)
      print ','.join(values)
