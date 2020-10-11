import os
import csv
from requests import get
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from csv import writer
from csv import reader
import json
from itertools import groupby

def jsonforshooju(url):

    #Let's download and unzip our file
    dirpath = os.getcwd ()
    url = urlopen (url)
    zipfile = ZipFile (BytesIO (url.read ()))
    zipfile.extractall (dirpath)
    zipfile.close ()

    with open ('jodi_gas_beta.csv') as csvin:
        readfile = csv.reader (csvin, delimiter=',')
        with open ('output_1.csv', 'w', newline='\n', encoding='utf-8') as csvout:
            writefile = csv.writer (csvout, delimiter=',', lineterminator='\n')
            for row in readfile:
                row.extend ([str (row[0]) + '-' + str (row[2]) + '-' + str (row[3]) + '-' + str (row[4])])
                row.extend (['[' + str (row[1]) + ', ' + str (row[5]) + ']'])
                del row[1] #deletar as colunas TIME_PERIOD
                del row[4] #deletar as colunas OBS_VALUE
                writefile.writerow (row)

    #mudar o nome das das duas ultimas colunas
    header = ['REF_AREA', 'ENERGY_PRODUCT', 'FLOW_BREAKDOWN', 'UNIT_MEASURE', 'ASSESSMENT_CODE', 'series_id', 'points']
    with open ('output_1.csv', 'r') as fp:
        reader = csv.DictReader (fp, fieldnames=header)
        with open ('output_2.csv', 'w', newline='\n') as fh:
            writer = csv.DictWriter (fh, fieldnames=reader.fieldnames)
            writer.writeheader ()
            header_mapping = next (reader)
            writer.writerows (reader)




    #criar o campo fields

    with open('output_2.csv') as csv_file:
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
    #groups = [json.dummps(groups) for record in json.load(in_j)]

    #criar o arquivo json
    with open ('JsonResult.json', 'w') as jsonfile:
        for d in groups:
            json.dump (d, jsonfile)
            jsonfile.write ('\n')


    #deletar as versões intermediárias de csv


    #








    # dirpath = os.getcwd()
    # raw_data = dirpath + "\jodi_gas_csv_beta\jodi_gas_beta.csv"
    #
    # #putting all data into a dataframe and creating a new column for series_id
    # df = pd.read_csv(raw_data)
    # df['series_id'] = df['REF_AREA'] + '-' + df['ENERGY_PRODUCT'] + '-' +  df['FLOW_BREAKDOWN']  + '-' +  df['UNIT_MEASURE'].map(str)
    #
    # #creating a time and assessment code array
    # df = df.assign(points = df[['TIME_PERIOD', 'ASSESSMENT_CODE']].values.tolist())
    #
    # #let´s use OBS_VALUE as additional field
    # df = df.rename(columns = {'OBS_VALUE':'field_obs_value'})
    #
    # #selecting only useful columns
    # df = pd.DataFrame(df, columns = ['series_id', 'points','field_obs_value'])
    #
    # #creating a NDJson also known as Json Line
    # df.to_json('JsonResult.json', orient = 'records', lines = True)

if __name__ == '__main__':
    url = "https://www.jodidata.org/_resources/files/downloads/gas-data/jodi_gas_csv_beta.zip"
    jsonforshooju (url)