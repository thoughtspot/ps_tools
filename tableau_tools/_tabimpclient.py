#%%
import pandas as pd
import numpy as np
import xmltodict, json
import xml.etree.ElementTree as et
#import tableauhyperio as hio
import os
import shutil
from pathlib import Path
from thoughtspot_tml.utils import determine_tml_type
from thoughtspot_tml import Table
import json
import re
from datetime import date
#%%
def connectiondetails(con):
    connectiondetails=con
    df1=pd.json_normalize(connectiondetails)
    df2=pd.json_normalize(connectiondetails)
    df1.rename(
        columns=({
    'Authentication': 'authentication'
    ,'connection.@authentication': 'authentication'      
    ,'@channel': 'channel'
    ,'connection.@class': 'class'
    ,'connection.@dbname': 'db'
    ,'@dbname': 'db'
    #,'@server-ds-friendly-name':'db'
    ,'connection.@schema':'schema'           
    ,'@server': 'server'
    ,'connection.@server':'server'           
    ,'connection.@username':'username'
    ,'connection.@warehouse':'warehouse'            
    ,'@name':'connection'
    ,'named-connection.@name':'connection'          
    ,'@directory':'directory'
    ,'connection.@directory':'directory'
    }),
        inplace=True,
    )
    df2.rename(
    columns=({
        'extract.connection.@authentication': 'authentication'  
        ,'connection.named-connections.named-connection.connection.@directory':'directory'
        ,'connection.named-connections.named-connection.connection.@class':'class'
        ,'connection.named-connections.named-connection.@name':'connection'  
        ,'named-connections.named-connection.connection.@directory':'directory'
        ,'named-connections.named-connection.@name':'connection'  
        ,'named-connections.named-connection.connection.@class':'class' 
    }),
        inplace=True,
    )  
    cols = ["authentication","class","db","schema","server","username","warehouse","connection","directory"]
    udfs = pd.concat([df1, df2], ignore_index=True)
    udfs = udfs.reindex(udfs.columns.union(cols, sort=False), axis=1, fill_value=" ")
    udfs=udfs.dropna(subset=['db'])
    for index, row in udfs.iterrows():
        if row['connection'] == ' ':
            udfs.at[index, 'connection'] = 'sqlproxy'    
    connections = udfs[["authentication","class","db","schema","server","username","warehouse","connection","directory"]]
    return connections
#%%
def datasourcedetails(dsd):
    datasourcedetails=dsd
    df1=pd.json_normalize(datasourcedetails)
    df2=pd.json_normalize(datasourcedetails)
    df1.rename(
        columns=({
        '@connection': 'connection'
        ,'@name': 'name'
        ,'@table': 'table'
        ,'@type': 'dstype'
    }),
        inplace=True,
    )
    df2.rename(
        columns=({
        'connection._.fcp.ObjectModelEncapsulateLegacy.false...relation.@connection': 'connection'
        ,'@caption': 'name'
        ,'connection._.fcp.ObjectModelEncapsulateLegacy.false...relation.@table': 'table'
        ,'connection._.fcp.ObjectModelEncapsulateLegacy.false...relation.@type': 'dstype'
    }),
        inplace=True,
    )
    cols = ["connection","name","table","dstype"]
    udfs = pd.concat([df1, df2], ignore_index=True)
    udfs = udfs.reindex(udfs.columns.union(cols, sort=False), axis=1, fill_value=" ")
    udfs=udfs.dropna(subset=['connection'])
    for index, row in udfs.iterrows():
        if row['connection'] == ' ':
            udfs.at[index, 'connection'] = 'sqlproxy' 
    datasources = udfs[["connection","name","table","dstype"]]
    return datasources
#%%
def tablemappingdetails(tblmap):
    tablemappingdetails=tblmap
    try:
        df = pd.json_normalize(tablemappingdetails)
        df.rename(
            columns=({ 
        '@caption': 'name'
        ,'@id': 'tableobject'
        ,'properties.relation.@connection': 'connection'
        ,'properties.relation.@table': 'table'}), 
            inplace=True,
        )
        df[['c1','c2']] = pd.DataFrame(df.properties.tolist(), index= df.index)
        df1 = pd.json_normalize(df['c1'])
        df2 = pd.json_normalize(df['c2'])
        union_dfs = pd.concat([df1, df2], ignore_index=True)
        union_dfs.rename(
            columns=({ 
        '@context': 'context'
        ,'relation.@connection': 'extractconnection'
        ,'relation.@name': 'name'
        ,'relation.@table': 'extracttable'
        ,'relation.@type': 'extracttype'}), 
            inplace=True,
        )
        cols = ["name", "tableobject"]
        df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=" ")
        objrels = df[["name", "tableobject"]]
        objectrelations = objrels.merge(union_dfs, on='name', validate='m:1')
        return objectrelations
    except: 
        df = pd.json_normalize(tablemappingdetails)
        df.rename(
            columns=({ 
        '@caption': 'name'
        ,'@id': 'tableobject'
        ,'properties.relation.@connection': 'connection'
        ,'properties.relation.@table': 'table'}), 
            inplace=True,
        )
        cols = ["name", "tableobject"]
        df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=" ")
        or1 = df[["name", "tableobject"]]
        #objectrelations.to_csv(os.path.join(tabfiledata,r'objectrelations.csv') )

        df = pd.json_normalize(tablemappingdetails)
        df['@caption1']=df['@caption']
        df.rename(
            columns=({ 
        '@caption': 'name'
        ,'@caption1': 'tableobject'
        ,'properties.relation.@connection': 'connection'
        ,'properties.relation.@table': 'table'}), 
            inplace=True,
        )
        cols = ["name", "tableobject"]
        df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=" ")
        or2 = df[["name", "tableobject"]]
        objectrelations = pd.concat([or1, or2], ignore_index=True)
        return objectrelations
#%%
def metadetails(mtd):
    metadetails=mtd
    df1=pd.json_normalize(metadetails)
    df2=pd.json_normalize(metadetails)
    df1.rename(
        columns=({
    'remote-alias':'col_name'
    ,'remote-name': 'db_column_name'
    ,'@class':'column_type'
    ,'aggregation': 'aggregation'
    ,'local-type': 'data_type'
    ,'caption': 'db_table'
    ,'_.fcp.ObjectModelEncapsulateLegacy.true...object-id':'tableobject'
    }), 
        inplace=True,
    )
    df2.rename(
        columns=({
    'remote-alias':'col_name'
    ,'remote-name': 'db_column_name'
    ,'@class':'column_type'
    ,'aggregation': 'aggregation'
    ,'local-type': 'data_type'
    ,'caption': 'db_table'
    ,'parent-name':'tableobject'
    }), 
        inplace=True,
    )
    union_dfs = pd.concat([df1, df2], ignore_index=True)
    cols = ["col_name", "db_column_name","column_type","aggregation","data_type","tableobject"]
    df = union_dfs.reindex(union_dfs.columns.union(cols, sort=False), axis=1, fill_value=" ")
    df['tableobject'] = df['tableobject'].str.strip('[]')
    metadata = df[["col_name", "db_column_name","column_type","aggregation","data_type","tableobject"]]
    #metadata=metadata.dropna(subset=['tableobject'])
    #metadata.to_csv(os.path.join(tabfiledata,r'metadata.csv') )
    return metadata
#%%
def tabledetails(tbl):
    tabledetails=tbl
    df = pd.json_normalize(tabledetails)
    df['@name'] = df['@name'].str.strip('[__tableau_internal_object_id__].')
    df['destination']=df['@name']
    df['destinationname']=df['@caption']
    df.rename(
        columns=({ 
    '@caption': 'db_table'
    ,'@datatype': 'datatype'
    ,'@name': 'tableobject'
    ,'@role': 'role'
    ,'@type': 'type'}), 
        inplace=True,
    )
    cols = ["db_table", "datatype", "tableobject"]
    df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=" ")
    tables = df[["db_table", "datatype", "tableobject"]]
    #tables.to_csv(os.path.join(tabfiledata,r'tables.csv') )
    return tables
#%%
def desttabledetails(destbl):
    desttabledetails=destbl
    df = pd.json_normalize(desttabledetails)
    df['@name'] = df['@name'].str.strip('[__tableau_internal_object_id__].')
    df['destination']=df['@name']
    df['destinationname']=df['@caption']
    df.rename(
        columns=({ 
    '@caption': 'db_table'
    ,'@datatype': 'datatype'
    ,'@name': 'tableobject'
    ,'@role': 'role'
    ,'@type': 'type'}), 
        inplace=True,
    )
    cols = ["destination","destinationname"]
    df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=" ")
    destinationtables = df[["destination","destinationname"]]
    #tables.to_csv(os.path.join(tabfiledata,r'tables.csv') )
    return destinationtables
#%%
def relationshipdetails(rel):
    relationshipdetails=rel
    try:
        #run for simple join structures    
        df = pd.json_normalize(relationshipdetails)
        df.rename(
            columns=({ 
        'expression.@op': 'op'
        ,'expression.expression': 'expression'
        ,'first-end-point.@object-id': 'tableobject'
        ,'second-end-point.@object-id': 'destination'}), 
            inplace=True,
        )
        df[['lk','rk']] = pd.DataFrame(df.expression.tolist(), index= df.index)
        df['lkey'] = pd.json_normalize(df['lk'])
        df['rkey'] = pd.json_normalize(df['rk'])
        df['lkey'] = df['lkey'].str.strip('[]')
        df['rkey'] = df['rkey'].str.strip('[]')
        df['type'] = 'INNER'
        cols = ["tableobject", "destination","op","lkey","rkey","type"]
        df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=" ")
        relationships = df[["tableobject", "destination","op","lkey","rkey","type"]]
        relationships = relationships.fillna('-')
        return relationships

    except:
        # run for complicated join structures
        df = pd.json_normalize(relationshipdetails)
        df.rename(
            columns=({ 
        'expression.@op': 'op'
        ,'expression.expression': 'expression'
        ,'first-end-point.@object-id': 'tableobject'
        ,'second-end-point.@object-id': 'destination'
        ,'first-end-point.@unique-key': 'tableobjectunqkey'
        ,'second-end-point.@unique-key': 'destinationunqkey'
        ,'expression.@_.fcp.InequalityRelationships.false...op' : 'ineqrelfalse'
        ,'expression.@_.fcp.InequalityRelationships.true...op': 'ineqreltrue'}), 
            inplace=True,
        )
        df
        df[['lk','rk']] = pd.DataFrame(df.expression.tolist(), index= df.index)
        df[['lkey','lkeyineqrelfalse','lkeyineqreltrue']] = pd.json_normalize(df['lk'])
        df[['rkey','rkeyineqrelfalse','rkeyineqreltrue']] = pd.json_normalize(df['rk'])
        cols = ["tableobject", "destination","op","lkey","rkey","tableobjectunqkey","destinationunqkey","ineqreltrue","ineqrelfalse","lkeyineqrelfalse","lkeyineqreltrue","rkeyineqrelfalse","rkeyineqreltrue"]
        df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=" ")
        relationships = df[["tableobject", "destination","op","lkey","rkey","tableobjectunqkey","destinationunqkey","ineqreltrue","ineqrelfalse","lkeyineqrelfalse","lkeyineqreltrue","rkeyineqrelfalse","rkeyineqreltrue"]]
        relationships = relationships.fillna('-')
        relationships['type'] =""
        relationships['is_one_to_one'] =""
        for index, row in relationships.iterrows():
            if row['destinationunqkey'] == 'true':
                relationships.at[index, 'is_one_to_one'] = 'true'
            else:
                relationships.at[index, 'is_one_to_one'] = 'false'

        for index, row in relationships.iterrows():
            if row['lkeyineqreltrue'] != '-' :
                relationships.at[index,'type']='LEFT OUTER' 
            elif row['rkeyineqreltrue'] != '-':
                relationships.at[index,'type']='RIGHT OUTER'
            elif row['op'] == '=':
                relationships.at[index,'type']='INNER'
            else:
                relationships.at[index,'type']='UNKNOWN'
        return relationships
#%%
def remap_expression(x):
    operations = ['add_months', 'add_years', 'diff_months', 'date_trunc']
    for operation in operations:
        pattern = re.compile(r"\b" + operation + r"\(\s*(\d+)\s*,\s*(\[.*?\])\s*\)")
        x = re.sub(pattern, operation + r"(\2, \1)", x)
    return x
def apply_remap_expression(x):
    try:
        return remap_expression(x)
    except:
        return x
def formuladetails(fml):
    formuladetails=fml
    try:
        df = pd.read_csv('config/Tab2TS_formulas.csv')
        mapping_df = df[["Tab_map","TS_map"]]
        validate_df = df[["Tab_map","Validate"]]
        df = pd.json_normalize(formuladetails)
        df.rename(
            columns=({ 
        '@caption': 'name'
        ,'@datatype': 'datatype'
        ,'@name': 'calcid'
        ,'@role': 'role'
        ,'calculation.@formula': 'formula'
        }), 
            inplace=True,
        )
        df['tsyntax'] = ""
        df['dataitem'] = ""
        df['addinfo'] = ""
        df['tsformula']=""
        df['validate']=""        
        cols = ["name", "datatype", "calcid", "role", "formula","tsyntax","dataitem","addinfo","validate"]
        df = df.reindex(df.columns.union(cols, sort=False), axis=1, fill_value=" ")
        df = df[["name", "datatype", "calcid", "role", "formula","tsyntax","dataitem","addinfo","validate"]]
        df=df.dropna(subset=['formula'])
        df = df.loc[df['name'].isin(['!Orders!','AVG','IF AND ELSEIF','DATEADD','RUNNING_AVG','DATETRUNC','DATEDIFF','NESTED','NESTEDIF','NESTED_LOOKUP'])]
        df['validate'] = df['formula'].apply(lambda x: 'Yes' if any(val in x for val in mapping_df['Tab_map']) else 'No')
        for i, row in df.iterrows():
            formula = row['formula']
            match = re.match(r"(\w+)\((.*)\)", formula)
            if match:
                df.at[i, 'tsyntax'] = match.group(1)
                dataitem = re.findall(r'\[(.*?)\]', match.group(2))
                df.at[i, 'dataitem'] = dataitem[0] if dataitem else ""
                addinfo = re.findall(r'\'(.*?)\'', match.group(2))
                df.at[i, 'addinfo'] = "'"+ addinfo[0]+"'" if addinfo else ""
        df['tsformula'] = df["formula"].replace(mapping_df.set_index('Tab_map')['TS_map'], inplace=True)
        df['tsformula'] = df["formula"].replace(mapping_df.set_index('Tab_map')['TS_map'])
        def replace_string(s):
            for Tab_map, TS_map in mapping_df.values:
                s = s.replace(Tab_map, TS_map)
            return s
        df['tsformula'] = df["formula"].apply(replace_string)
        df['expr'] = df['tsformula'].str.replace('~','')
        df['expr'] = df['expr'].apply(lambda x: remap_expression(x))
        formulas=df
        #formulas.to_csv(os.path.join(tabfiledata,r'formulas.csv') ) 
        return formulas
    except: pass
    return formulas

#%% #ANSWERS


#%%
#LIVEBOARDS
print('success')