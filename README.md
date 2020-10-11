<h1 align="center">
Shooju Technical Evaluation
</h1>

The goal is to create a single python2/3 file that uses only standard libraries that:

Uses only the URL https://www.jodidata.org/_resources/files/downloads/gas-data/jodi_gas_csv_beta.zip as input
Downloads, unzips, parses based on that single URL input
Writes to stdout a new line delimited (\n) JSON series-by-series representation of the input CSV

Each JSON series representation should be an object with 3 keys:

<ol>
<li>series_id: some unique series id; it should be meaningful to the series it is identifying</li>
<li>points: an array of date(time)/float arrays; the date(time) should be in ISO format as defined at https://en.wikipedia.org/wiki/ISO_8601.</li>
<li>fields: an object of any additional metadata available at the source that helps to describe and identify the data; a series representing Brazilian GDP might have two main keys: "country" and "concept" as in the example below</li>
</ol>


--------------------------------------------------

<h2 align="center">
Solution VERSION 2
</h2>

## Como usar:

Instale a versão 3.x do Python e o Virtualenv:

<ol>
<li> Clone este repositório : git clone https://github.com/DeboraOliver/-Shju_tech_test_VERSION_2
<li> Vá para o repositório : cd -Shju_tech_test_VERSION_2
<li> Run the main.py
</ol>

## Libraries Required

For this version ONLY standard libraries available on Python 3.8:

<ul>
<li>import csv</li>
<li>import json</li>
<li>import os</li>
<li>from datetime import datetime as dt</li>
<li>from io import BytesIO</li>
<li>from itertools import groupby</li>
<li>from urllib.request import urlopen</li>
<li>from zipfile import ZipFile</li>
</ul>

## Download, Unzip and Extract

Contrary of the first version of the this project, downloading, unziping and the extraction of csv file was possible due to zipfile library:

	def downloadzip(url):

		dirpath = os.getcwd ()
		url = urlopen (url)
		zipfile = ZipFile (BytesIO (url.read ()))
		zipfile.extractall (dirpath)
		zipfile.close ()

In the first version, it could all be done using a third party library named dload. Thus, instead of six lines of code we only used one. 

## Using ISO 8601 to formate date fields

As required the TIME_PERIOD column had to be in ISO 8601 format (Y-%m-%d). 

	def isoformate(date):
		def _dict(desc, date):
			return {'error': desc, 'ISO': date}

		for format in [('%Y-%m', 'Missing day')]:
			_dt = dt.strptime (date, format[0])
			return _dict (format[1], _dt.strftime ('%Y-%m-%d'))
			
In the given data, all entries had day missing. So, the function above is called to validate the time_period column:

	def validadedate():
	    with open ('jodi_gas_beta.csv') as fh_in, open ('output_1.csv', 'w') as fh_out:
		csv_reader = csv.DictReader (fh_in)
		csv_writer = csv.DictWriter (fh_out,
					     fieldnames=csv_reader.fieldnames +
							['error', 'ISO'])
		csv_writer.writeheader ()

		for row, values in enumerate (csv_reader, 2):
		    values.update (isoformate (values['TIME_PERIOD']))
				(...)
		
		
## Creating series_id field and points array

Series_id: is an identifying fiels, therefore each entry has to be unique. It is possible when it concatenates a few information such as REF_AREA, ENERGY_PRODUCT, FLOW_BREAKDOWN and UNIT_MEASURE.
Points :is an array containing the date in ISO format and a float value, OBS_VALUE.

	def cleanse():
	    with open ('output_1.csv') as csvin:
		readfile = csv.reader (csvin, delimiter=',')
		with open ('output_2.csv', 'w', newline='\n', encoding='utf-8') as csvout:
		    writefile = csv.writer (csvout, delimiter=',', lineterminator='\n')
		    for row in readfile:
			header_mapping = next (readfile)
			row.extend ([str(row[0]) + '-' + str (row[2]) + '-' + str (row[3]) + '-' + str (row[4])])
			row.extend (['[' + str (row[8]) + ', ' + str (row[5]) + ']'])
			del row[1] #delete TIME_PERIOD
			del row[4] #delete OBS_VALUE
			del row[5] #delete error
			del row[5]  #delete iSO
			writefile.writerow (row)

 Lastly, it deletes some coluns that won't be necessary. After it all is done, the only point missing is to name these new columns (series_id, points):
 
	def rename():
	    #renaming the last two columns
	    header = ['REF_AREA', 'ENERGY_PRODUCT', 'FLOW_BREAKDOWN', 'UNIT_MEASURE', 'ASSESSMENT_CODE', 'series_id', 'points']
	    with open ('output_2.csv', 'r') as fp:
		reader = csv.DictReader (fp, fieldnames=header)
		with open ('output_3.csv', 'w', newline='\n') as fh:
		    writer = csv.DictWriter (fh, fieldnames=reader.fieldnames)
		    writer.writeheader ()
		    header_mapping = next (reader)
		    writer.writerows (reader)
			
## Fields field

The lastfield to be created in the "Fields":

	def from_csv_to_json():
	    with open('output_3.csv') as csv_file:
		r = csv.DictReader(csv_file, skipinitialspace=True)
		data = [dict(d) for d in r]

		groups =[]

		for k,g in groupby(data, lambda r: (r['series_id'], r['points'])):
		    groups.append({
			"series_id": k[0],
			"points": k[1],
			"fields":[{k: v for k, v in d.items() if k not in ['series_id','points']} for d in list(g)]
		    })
			
## The newline-delimited Json

 A ndJSON is a collection of JSON objects, separated by '\n': 
 
	with open ('JsonResult.json', 'w') as jsonfile:
		for d in groups:
		    json.dump (d, jsonfile)
		    jsonfile.write ('\n')


# Sources

<ul>
<li><a href="https://docs.python.org/3/library/">Standard Library Python 3.8</a></li>
<li><a href="https://en.wikipedia.org/wiki/Time_series"> ISO_8601</a></li>
