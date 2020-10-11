import csv
import json
import os
from datetime import datetime as dt
from io import BytesIO
from itertools import groupby
from urllib.request import urlopen
from zipfile import ZipFile


def downloadzip(url):

    #Let's download and unzip our file
    dirpath = os.getcwd ()
    url = urlopen (url)
    zipfile = ZipFile (BytesIO (url.read ()))
    zipfile.extractall (dirpath)
    zipfile.close ()

#iso 8601 to formate date
def isoformate(date):
    def _dict(desc, date):
        return {'error': desc, 'ISO': date}

    for format in [('%Y-%m', 'Missing day')]:
        _dt = dt.strptime (date, format[0])
        return _dict (format[1], _dt.strftime ('%Y-%m-%d'))

def validadedate():
    with open ('jodi_gas_beta.csv') as fh_in, open ('output_1.csv', 'w') as fh_out:
        csv_reader = csv.DictReader (fh_in)
        csv_writer = csv.DictWriter (fh_out,
                                     fieldnames=csv_reader.fieldnames +
                                                ['error', 'ISO'])
        csv_writer.writeheader ()

        for row, values in enumerate (csv_reader, 2):
            values.update (isoformate (values['TIME_PERIOD']))

            # Show only Invalid Dates
            if any (w in values['error']
                    for w in ['Unknown', 'No Digit', 'missing']):
                print ('{:>3}: {v[TIME_PERIOD]:13.13} {v[error]:<22} {v[ISO]}'.
                       format (row, v=values))

            csv_writer.writerow (values)


def cleanse():
    with open ('output_1.csv') as csvin:
        readfile = csv.reader (csvin, delimiter=',')
        with open ('output_2.csv', 'w', newline='\n', encoding='utf-8') as csvout:
            writefile = csv.writer (csvout, delimiter=',', lineterminator='\n')
            for row in readfile:
                header_mapping = next (readfile)
                row.extend ([str(row[0]) + '-' + str (row[2]) + '-' + str (row[3]) + '-' + str (row[4])])
                row.extend (['[' + str (row[8]) + ', ' + str (row[5]) + ']'])
                del row[1] #deletar as colunas TIME_PERIOD
                del row[4] #deletar as colunas OBS_VALUE
                del row[5] #deletar as colunas error
                del row[5]  #deletar as colunas iSO
                writefile.writerow (row)

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


    #creating fields
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
    print(json.dumps(groups[:10], indent=4))

    #creating a NDjsonfile

    with open ('JsonResult.json', 'w') as jsonfile:
        for d in groups:
            json.dump (d, jsonfile)
            jsonfile.write ('\n')






if __name__ == '__main__':
    url = "https://www.jodidata.org/_resources/files/downloads/gas-data/jodi_gas_csv_beta.zip"
    downloadzip (url) #downloading and unzip
    validadedate() #puts date in iso8601 formate
    cleanse() #cleans unused columns while creating series_id and points
    rename() # naming columns properly
    from_csv_to_json () #creates a jsonfile