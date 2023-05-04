#%% LOAD LIBRARIES
from typing import List
from typing import Any
import datetime as dt
import logging
import pathlib
import pandas as pd
import toml
import typer
import pytz
import os
from cli._util import State
from cli._ux import comment, console, output_message
from pathlib import Path
from string import Template
import time
from subprocess import check_output
import pandas as pd
import numpy as np
import xmltodict
import os
import shutil
from pathlib import Path
from thoughtspot_tml.utils import determine_tml_type
from thoughtspot_tml import Table
from thoughtspot_tml import Worksheet
from thoughtspot_tml import Answer
import string
import random
import json
from thoughtspot_rest_api_v1 import *
import requests
import urllib3

urllib3.disable_warnings()
par_path = os.getcwd()

#%%
def ras(length):
    return ''.join(
        random.choice('a'+'b'+'c'+'d'+'e'+'f' + string.digits)
        for _ in range(length)
    )

#%%
def create_spotapp(tds_file_name):
    #tds_file_name = 'SF Trial.tds'
    print(par_path)

# LOAD FILES
    try: 
        con_metadata = pd.read_csv("{}/input/metadata_objects/metadata_{}.csv".format(par_path,tds_file_name))
    except: 
        pass
        #console.print('There are no metadata records (connectionstablesmetadata.csv) for this tds input',style= 'error')

    try: 
        con_relationships = pd.read_csv('{}/input/relationships/relations_{}.csv'.format(par_path,tds_file_name))
    except: 
        pass
        #console.print('There are no relationships (con_relationships.csv) for this tds input',style= 'error')

    try: 
        con_formulas = pd.read_csv('{}/input/formulas/formulas_{}.csv'.format(par_path,tds_file_name))
    except: 
        pass

    ##Get tables

    a=con_metadata[['db','schema','warehouse','db_table']].drop_duplicates()

    ## Get columns for each table

    b=con_metadata[['db','schema','warehouse','db_table','db_column_name','col_name','data_type']].drop_duplicates()

    ## Get formulas
    try:
        z=con_formulas[['name','expr']].drop_duplicates()
    except: pass

    #datatype mapping

    datatype_mapping = {'tableau': ['integer', 'date', 'string', 'real'],
                        'TS_data_type': ['INT64', 'DATE', 'VARCHAR', 'DOUBLE']}   
    df_types = pd.DataFrame(datatype_mapping) 

    # enrich data by TS data types

    b = b.merge(df_types, left_on='data_type', right_on='tableau')

    # aggregation mapping (WIP)

    aggr_mapping = {'aggr_type': ['INT64', 'DATE', 'VARCHAR', 'DOUBLE','INT32'], 
                    'TS_aggr': ['SUM', 'COUNT', 'COUNT', 'SUM','SUM']}

    aggr_types = pd.DataFrame(aggr_mapping)

    b = b.merge(aggr_types, left_on='TS_data_type', right_on='aggr_type')

    # column type mapping (WIP)

    column_type_mapping = {'col_type': ['INT64', 'DATE', 'VARCHAR', 'DOUBLE','INT32'], 
                    'TS_col_type': ['MEASURE', 'ATTRIBUTE', 'ATTRIBUTE', 'MEASURE','MEASURE']}  

    column_type_types = pd.DataFrame(column_type_mapping)
    b = b.merge(column_type_types, left_on='TS_data_type', right_on='col_type')


    #%% TABLE TMLS
    tml_cls=determine_tml_type(path='{}/config/TEMPLATE.table.tml'.format(par_path))
    tml=tml_cls.load(path='{}/config/TEMPLATE.table.tml'.format(par_path))
    tmldict = tml.to_dict()
    columntemplate = tmldict['table']['columns'][0]
    relationtemplate = tmldict['table']['joins_with'][0]
    cleantemplate = columntemplate

    new_path = par_path + "/output/TML/{}".format(tds_file_name)
    isExist = os.path.exists(new_path)
    if not isExist:
        os.makedirs(new_path)
    console.print("Creating SpotApp for {}...".format(tds_file_name),style = 'success')

    for table in range(len(a)):
        d = con_relationships
        e = d.loc[(d['name'] == a['db_table'].iloc[table])]
        if len(e) >= 1:
            tml=tml_cls.load(path='{}/config/TEMPLATE.table.tml'.format(par_path))    
            tmldict = tml.to_dict()
        else:
            tml=tml_cls.load(path='{}/config/TEMPLATE_NO_JOIN.table.tml'.format(par_path))    
            tmldict = tml.to_dict()
        tmldict['guid'] = 'INVALID'
        tmldict['table']['name']=a['db_table'].iloc[table]
        tmldict['table']['db']=a['db'].iloc[table]
        tmldict['table']['schema']=a['schema'].iloc[table]
        tmldict['table']['db_table']=a['db_table'].iloc[table]
        tmldict['table']['connection']['name']='SF Trial'
        ## TEST
        
        if len(e) >= 1:
            for rel in range(len(e)-1):
                tmldict['table']['joins_with'].append(relationtemplate)
            for join in range(len(e)):
                tmldict['table']['joins_with'][join]['name'] = e['name'].iloc[join] + '_'+e['destinationname'].iloc[join]
                tmldict['table']['joins_with'][join]['destination']['name'] = e['destinationname'].iloc[join]
                tmldict['table']['joins_with'][join]['on'] = e['on'].iloc[join]
                tmldict['table']['joins_with'][join]['type'] = e['type'].iloc[join]
        else:
            pass
        #tmldict['table']['joins_with'][0]['is_one_to_one'] = False
            
        ## TEST END
        console.print("TABLE: "+ tmldict['table']['name'],style ='main')
        c = b.loc[(b['db_table'] == a['db_table'].iloc[table])]
        print("Number of columns: "+str(len(c)))
        for column in range(len(c)-1):
            columntemplate = cleantemplate
            columntemplate['db_column_name'] = c['db_column_name'].iloc[column]
            #columntemplate['db_column_properties']['data_type'] = 'VARCHAR'
            tmldict['table']['columns'].append(columntemplate)
            Table.loads(json.dumps(tmldict)).dump("{}/output/TML/staging/{}.table.tml".format(par_path,a['db_table'].iloc[table]))
            ####### --------- #######
            tml=tml_cls.load(path='{}/output/TML/staging/{}.table.tml'.format(par_path,a['db_table'].iloc[table]))
            tmldict = tml.to_dict()
            random_guid = ras(8) +'-'+ ras(4)+'-'+ ras(4)+'-'+ ras(4) +'-'+ ras(12)
            tmldict['guid'] = random_guid
        for column in range(len(tmldict['table']['columns'])):
            tmldict['table']['columns'][column]['db_column_name'] = c['db_column_name'].iloc[column]
            tmldict['table']['columns'][column]['properties']['column_type'] = c['TS_col_type'].iloc[column]
            tmldict['table']['columns'][column]['properties']['aggregation'] = c['TS_aggr'].iloc[column]
            tmldict['table']['columns'][column]['name'] = c['col_name'].iloc[column]
            tmldict['table']['columns'][column]['db_column_properties']['data_type'] = c['TS_data_type'].iloc[column]
            #print(column)
            #print('----> ' + c['db_column_name'].iloc[column])
        Table.loads(json.dumps(tmldict)).dump("{}/output/TML/{}/{}.table.tml".format(par_path,tds_file_name,a['db_table'].iloc[table]))
        
        ws = Table.load(path = "{}/output/TML/{}/{}.table.tml".format(par_path,tds_file_name,a['db_table'].iloc[table]))
        data = ws.dumps(format_type="JSON")
        data_s = json.loads(data)
        import_object = json.dumps(tmldict)
        
    #print("_______________________________________________")
    #%% WORKSHEET TMLS
    ### Worksheet
    #Load Template
    tml_ws=determine_tml_type(path='{}/config/TEMPLATE.worksheet.tml'.format(par_path))
    worksheet=tml_ws.load(path='{}/config/TEMPLATE.worksheet.tml'.format(par_path))
    worksheet = worksheet.to_dict()
    
    #General Information
    worksheet['guid'] = ''
    worksheet['worksheet']['name'] = a['db'][0]
    worksheet['worksheet']['properties']['is_bypass_rls'] = False
    worksheet['worksheet']['properties']['join_progressive'] = True 
    
    #Templates:
    table_template = worksheet['worksheet']['tables'][0]
    join_template = worksheet['worksheet']['joins'][0]
    col_template = worksheet['worksheet']['worksheet_columns'][0]
    tbl_path_template = worksheet['worksheet']['table_paths'][0]
    form_template = worksheet['worksheet']['formulas'][0]
    #join_path_template = worksheet['worksheet']['table_paths'][0]['join_path'][0]['join']
    
    #Generate Worksheet

    for tbl in range(len(a)-1):
        worksheet['worksheet']['tables'].append(table_template)
        worksheet['worksheet']['table_paths'].append(tbl_path_template)
        
    Worksheet.loads(json.dumps(worksheet)).dump("{}.worksheet.tml".format(a['db'].iloc[0]))          
    tml=Worksheet.load(path='{}.worksheet.tml'.format(a['db'].iloc[0]))
    worksheet = tml.to_dict()
    
    for n in range(len(a)):
        worksheet['worksheet']['tables'][n]['name'] = a['db_table'].iloc[n]
        worksheet['worksheet']['tables'][n]['id'] = None #a['db_table'].iloc[n]
        worksheet['worksheet']['tables'][n]['fqn'] = None #a['db_table'].iloc[n]
        
        worksheet['worksheet']['table_paths'][n]['id'] = a['db_table'].iloc[n] + '_1'
        worksheet['worksheet']['table_paths'][n]['table'] = a['db_table'].iloc[n]

        try:
            jp = pd.read_csv("{}/input/join_paths/path_{}.csv".format(par_path,tds_file_name))
            f = jp.loc[(jp['destinationname'] == a['db_table'].iloc[n])]
            for i in range(len(f)):
                #print(f['join_path'].iloc[i])
                worksheet['worksheet']['table_paths'][n]['join_path'][0]['join'].append(f['path_values'].iloc[i])
            worksheet['worksheet']['table_paths'][n]['join_path'][0]['join'].remove("DEFAULT")
        except Exception as e: 
            pass
            print(str(e))

    for jn in range(len(d)-1):
        worksheet['worksheet']['joins'].append(join_template)

    Worksheet.loads(json.dumps(worksheet)).dump("{}.worksheet.tml".format(d['db'].iloc[0]))          
    tml=Worksheet.load(path='{}.worksheet.tml'.format(d['db'].iloc[0]))
    worksheet = tml.to_dict()

    for jn in range(len(d)):
        worksheet['worksheet']['joins'][jn]['id'] = None#d['name'].iloc[jn] + '_'+d['destinationname'].iloc[jn]
        worksheet['worksheet']['joins'][jn]['name'] = d['name'].iloc[jn] + '_'+d['destinationname'].iloc[jn]
        worksheet['worksheet']['joins'][jn]['source'] = d['name'].iloc[jn]
        worksheet['worksheet']['joins'][jn]['destination'] = d['destinationname'].iloc[jn]
        worksheet['worksheet']['joins'][jn]['type'] = d['type'].iloc[jn]
        worksheet['worksheet']['joins'][jn]['is_one_to_one'] = False
#%% WORKSHEET - COLUMNS
        
    #worksheet['worksheet']['table_paths'][0]['join_path'][0]['join'] = None
    #worksheet['worksheet']['table_paths'][0]['column'] = None

    for column in range(len(b)-1):
        worksheet['worksheet']['worksheet_columns'].append(col_template)

    Worksheet.loads(json.dumps(worksheet)).dump("{}.worksheet.tml".format(b['db'].iloc[0]))          
    tml=Worksheet.load(path='{}.worksheet.tml'.format(b['db'].iloc[0]))
    worksheet = tml.to_dict()

    for column in range(len(b)):
        worksheet['worksheet']['worksheet_columns'][column]['name'] = b['db_column_name'][column]
        worksheet['worksheet']['worksheet_columns'][column]['column_id'] = b['db_table'][column]+'_1::'+b['db_column_name'][column]
        worksheet['worksheet']['worksheet_columns'][column]['formula_id'] = None
        worksheet['worksheet']['worksheet_columns'][column]['properties']['column_type'] = b['TS_col_type'][column]
        worksheet['worksheet']['worksheet_columns'][column]['properties']['aggregation'] = b['TS_aggr'][column]
        worksheet['worksheet']['worksheet_columns'][column]['properties']['index_type'] = None#'DONT_INDEX'

#%% WORKSHEET - FORMULAS
    try:
        for formulas in range(len(z)-1):
            worksheet['worksheet']['formulas'].append(form_template)

        Worksheet.loads(json.dumps(worksheet)).dump("{}.worksheet.tml".format(z['name'].iloc[0]))          
        tml=Worksheet.load(path='{}.worksheet.tml'.format(z['name'].iloc[0]))
        worksheet = tml.to_dict()

        for formulas in range(len(z)):
            worksheet['worksheet']['formulas'][formulas]['id'] = None
            worksheet['worksheet']['formulas'][formulas]['name'] = z['name'][formulas]
            worksheet['worksheet']['formulas'][formulas]['expr'] = z['expr'][formulas]
            worksheet['worksheet']['formulas'][formulas]['properties'] = None
            worksheet['worksheet']['formulas'][formulas]['was_auto_generated'] = False
    except:
        print('There are no formulas') 
        pass

    Worksheet.loads(json.dumps(worksheet,indent=4)).dump("{}/output/TML/{}/{}.worksheet.tml".format(par_path,tds_file_name,tds_file_name))