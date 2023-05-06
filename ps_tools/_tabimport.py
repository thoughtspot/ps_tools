#%%
from cli._ux import comment, console, output_message
from ._tabimpclient import *
def parse_tableau(filename):
    filecount = 0
    tds_directory = './input/tds/'
#for filename in os.listdir(tds_directory):
    if filename.endswith(".tds"): #".tds"=default
        filecount += 1
        fileid = 'tdsid'+str(filecount)
        print(os.path.join(tds_directory, filename))
        tabfile = os.path.join(tds_directory, filename)
        with open(tabfile, 'r') as myfile:
            obj = xmltodict.parse(myfile.read())

# Parsing through different levels in the xml to find the required information such as connections
        try:
            con = obj['datasource'][1]['connection']['named-connections']['named-connection']
        except: pass
        try:
            con = obj['datasource']['connection']['named-connections']['named-connection']
        except: pass 
        try:
            con = obj['datasources']['datasource']['connection']
        except: pass
        try:
            dsd = obj['datasource'][1]['connection']['_.fcp.ObjectModelEncapsulateLegacy.true...relation']['relation']
        except: pass
        try:
            dsd = obj['datasource']['connection']['_.fcp.ObjectModelEncapsulateLegacy.true...relation']
        except: pass
        try:
            dsd = obj['datasource']['connection']['_.fcp.ObjectModelEncapsulateLegacy.true...relation']['relation']
        except: pass
        try:
            tblmap = obj['datasource'][1]['_.fcp.ObjectModelEncapsulateLegacy.true...object-graph']['objects']['object']
        except: pass
        try:
            tblmap = obj['datasource']['_.fcp.ObjectModelEncapsulateLegacy.true...object-graph']['objects']['object']
        except: pass
        try:
            mtd = obj['datasource'][1]['connection']['metadata-records']['metadata-record']
        except: pass
        try:
            mtd = obj['datasource']['connection']['metadata-records']['metadata-record']
        except: pass
        try:
            tbl = obj['datasource'][1]['_.fcp.ObjectModelTableType.true...column']
        except: pass
        try:
            tbl = obj['datasource']['_.fcp.ObjectModelTableType.true...column']
        except: pass
        try: 
            destbl = obj['datasource'][1]['_.fcp.ObjectModelTableType.true...column']
        except: pass
        try:
            destbl = obj['datasource']['_.fcp.ObjectModelTableType.true...column']
        except: pass
        try:
            rel = obj['datasource'][1]['_.fcp.ObjectModelEncapsulateLegacy.true...object-graph']['relationships']['relationship']
        except: pass
        try:
            rel = obj['datasource']['_.fcp.ObjectModelEncapsulateLegacy.true...object-graph']['relationships']['relationship']
        except: pass
        try: 
            fml = obj['datasource'][1]['column']
        except: pass
        try:
            fml = obj['datasource']['column']
        except: pass
# Referencing the functions from the _tabimpclient.py file
        try:
            connections = connectiondetails(con)
        except:
            output_message('No connections for ' + filename, "error") 
            pass 
        try:
            datasources = datasourcedetails(dsd)
        except:
            output_message('No datasources for ' + filename, "error")  
            pass             
        try:
            objectrelations=tablemappingdetails(tblmap)
        except: 
            output_message('No objectrelations for ' + filename, "error") 
            pass 
        try:
            metadata = metadetails(mtd)
        except: 
            output_message('No metadata for ' + filename, "error") 
            pass 
        try:
            tables = tabledetails(tbl)
        except: 
            output_message('No tables for ' + filename, "error") 
            pass 
        try:
            destinationtables = desttabledetails(destbl)
        except: 
            output_message('No destinationtables for ' + filename, "error") 
            pass 
        try:
            relationships = relationshipdetails(rel)
        except: 
            output_message('No relationships for ' + filename, "error") 
            pass 
        try:
            formulas = formuladetails(fml)
        except: 
            output_message('No formulas for ' + filename, "error") 
            pass 
# Joining multiple dataframes together ready for the CSV output
        try:    
            connectionsources = connections.merge(datasources, on='connection', validate='1:m')
        except: pass
        try:    
            connectionsources = connections.merge(datasources, on='connection', validate='m:m')
        except: pass
        try:
            connectionobjects= connectionsources.merge(objectrelations, on='name', how='right', validate='1:m')
        except: pass
        try:
            connectionobjects= connectionsources.merge(objectrelations, on='name', how='right', validate='m:m')
        except: pass
        connectionobjectsmeta = connectionobjects.merge(metadata, on='tableobject', validate='1:m')
        tablesmetadata = metadata.merge(tables, on='tableobject', validate='m:1')
        connectionstablesmetadata = tablesmetadata.merge(connectionobjects, on='tableobject', validate='m:1')

        try:
            df = connectionstablesmetadata[["col_name","db_table"]]
            df = df.copy()
            df.loc[:, 'tablecolumn'] = df['db_table'] + '_1::' + df['col_name']
            for index, row in df.iterrows():
                formulas['expr'] = formulas['expr'].str.replace(row['col_name'], row['tablecolumn'])
        except: pass

        try:
            connectionobjsrels = connectionobjects.merge(relationships, on='tableobject', validate='1:m')
        except: pass
        try:
            connectionobjectsrelationships = connectionobjsrels.merge(destinationtables, on='destination', validate='m:1')
        except: pass
        try:
            connectionobjectsrelationships['on']='[' + connectionobjectsrelationships['name']+ '::' + connectionobjectsrelationships['lkey'] + '] ' + connectionobjectsrelationships['op'] + ' [' + connectionobjectsrelationships['destinationname']+ '::' + connectionobjectsrelationships['rkey'] + ']'   
        except: pass
        connectionstablesmetadata['filename']=filename
        connectionstablesmetadata['fileid']= fileid
        connectionstablesmetadata.to_csv('./input/metadata_objects/metadata_{}.csv'.format(filename),index=False )
        
        try:
            connectionobjectsrelationships['filename']=filename
            connectionobjectsrelationships['fileid']= fileid
            connectionobjectsrelationships.to_csv('./input/relationships/relations_{}.csv'.format(filename),index=False )
        except: output_message('There are no relationships for ' + filename, "error")

        try:
            data = connectionobjectsrelationships
            data['join_path'] = data['name'] + '_' + data['destinationname']
            rel = data[['name','destinationname','join_path']]
            par = data[['name','destinationname','join_path']]
            df = rel.merge(par, how='right', left_on='destinationname', right_on='name')
            df2 = df.merge(rel, how='right', left_on='destinationname_y', right_on='name')
            df3 = df2[['destinationname','join_path_x','join_path_y','join_path']]
            df_unpivoted = df3.melt(id_vars=['destinationname'], var_name='paths', value_name='path_values')
            df_unpivoted.dropna(inplace=True)
            join_paths = df_unpivoted[['destinationname','path_values']] 
            join_paths.to_csv('./input/join_paths/path_{}.csv'.format(filename),index=False)
        except: output_message('There are no join paths for ' + filename, "error")
        try: 
            formulas['filename']=filename
            formulas['fileid']= fileid
            formulas.to_csv('./input/formulas/formulas_{}.csv'.format(filename),index=False )
        except: output_message('There are no formulas for ' + filename, "error")
# Summary CSV output provided to list the various files that have been parsed 
        df = connectionstablesmetadata[["db_table","db","schema","connection","fileid"]].drop_duplicates()
        for index, row in df.iterrows():
            db_table = row['db_table']
            db = row['db']
            schema = row['schema']
            connection = row['connection']
            details = pd.DataFrame(columns=["filename", "filecount","fileid","db_table","db","schema","connection"])
            new_details = pd.DataFrame({"filename": [filename], "filecount": [filecount], "fileid": [fileid], "db_table": [db_table], "db": [db], "schema": [schema], "connection": [connection]})
            details = pd.concat([details, new_details], ignore_index=True)

#%% ### TWB files
    twb_directory = './input/twb/'
#for filename in os.listdir(twb_directory):
    if filename.endswith(".twb"): #".twb"=default
        filecount += 1
        fileid = 'twbid'+str(filecount)
        print(os.path.join(twb_directory, filename))
        tabfile = os.path.join(twb_directory, filename)
        with open(tabfile, 'r') as myfile:
            obj = xmltodict.parse(myfile.read())
# Parsing through different levels in the xml to find the required information such as connections       
        try:
            con = obj['workbook']['datasources']['datasource'][1]['connection']['named-connections']['named-connection']
        except: pass
        try:
            con = obj['workbook']['datasources']['datasource']['connection']['named-connections']['named-connection']
        except: pass
        try:
            con = obj['workbook']['datasources']['datasource']['connection']
        except: pass
        try:
            dsd = obj['workbook']['datasources']['datasource'][1]['connection']['_.fcp.ObjectModelEncapsulateLegacy.true...relation']
        except: pass
        try:
            dsd = obj['workbook']['datasources']['datasource'][1]['connection']['_.fcp.ObjectModelEncapsulateLegacy.true...relation']['relation']
        except: pass
        try:
            dsd = obj['workbook']['datasources']['datasource']['connection']['_.fcp.ObjectModelEncapsulateLegacy.true...relation']
        except: pass
        try:
            dsd = obj['workbook']['datasources']['datasource']['connection']['_.fcp.ObjectModelEncapsulateLegacy.true...relation']['relation']
        except: pass
        try:
            tblmap = obj['workbook']['datasources']['datasource'][1]['_.fcp.ObjectModelEncapsulateLegacy.true...object-graph']['objects']['object']
        except: pass
        try:
            tblmap = obj['workbook']['datasources']['datasource']['_.fcp.ObjectModelEncapsulateLegacy.true...object-graph']['objects']['object']
        except: pass
        try:
            mtd = obj['workbook']['datasources']['datasource'][1]['connection']['metadata-records']['metadata-record']
        except: pass
        try:
            mtd = obj['workbook']['datasources']['datasource']['connection']['metadata-records']['metadata-record']
        except: pass
        try:
            tbl = obj['workbook']['datasources']['datasource'][1]['_.fcp.ObjectModelTableType.true...column']
        except: pass
        try:
            tbl = obj['workbook']['datasources']['datasource']['_.fcp.ObjectModelTableType.true...column']
        except: pass
        try: 
            destbl = obj['workbook']['datasources']['datasource'][1]['_.fcp.ObjectModelTableType.true...column']
        except: pass
        try:
            destbl = obj['workbook']['datasources']['datasource']['_.fcp.ObjectModelTableType.true...column']
        except: pass
        try:
            rel = obj['workbook']['datasources']['datasource'][1]['_.fcp.ObjectModelEncapsulateLegacy.true...object-graph']['relationships']['relationship']
        except: pass
        try:
            rel = obj['workbook']['datasources']['datasource']['_.fcp.ObjectModelEncapsulateLegacy.true...object-graph']['relationships']['relationship']
        except: pass
        try: 
            fml = obj['workbook']['datasources']['datasource'][1]['column']
        except: pass
        try:
            fml = obj['workbook']['datasources']['datasource']['column']
        except: pass
# Referencing the functions from the _tabimpclient.py file
        try:
            connections = connectiondetails(con)
        except:
            output_message('No connections for ' + filename, "error") 
            pass 
        try:
            datasources = datasourcedetails(dsd)
        except:
            output_message('No datasources for ' + filename, "error")  
            pass             
        try:
            objectrelations=tablemappingdetails(tblmap)
        except: 
            output_message('No objectrelations for ' + filename, "error") 
            pass 
        try:
            metadata = metadetails(mtd)
        except: 
            output_message('No metadata for ' + filename, "error") 
            pass 
        try:
            tables = tabledetails(tbl)
        except: 
            output_message('No tables for ' + filename, "error") 
            pass 
        try:
            destinationtables = desttabledetails(destbl)
        except: 
            output_message('No destinationtables for ' + filename, "error") 
            pass 
        try:
            relationships = relationshipdetails(rel)
        except: 
            output_message('No relationships for ' + filename, "error") 
            pass 
        try:
            formulas = formuladetails(fml)
        except: 
            output_message('No formulas for ' + filename, "error") 
            pass 
# Joining multiple dataframes together ready for the CSV output
        try:    
            connectionsources = connections.merge(datasources, on='connection', validate='1:m')
        except: pass
        try:    
            connectionsources = connections.merge(datasources, on='connection', validate='m:m')
        except: pass
        try:
            connectionobjects= connectionsources.merge(objectrelations, on='name', how='right', validate='1:m')
        except: pass
        try:
            connectionobjects= connectionsources.merge(objectrelations, on='name', how='right', validate='m:m')
        except: pass
        connectionobjectsmeta = connectionobjects.merge(metadata, on='tableobject', validate='1:m')
        tablesmetadata = metadata.merge(tables, on='tableobject', validate='m:1')

        connectionstablesmetadata = tablesmetadata.merge(connectionobjects, on='tableobject', validate='m:1')
        try:
            df = connectionstablesmetadata[["col_name","db_table"]]
            df = df.copy()
            df.loc[:, 'tablecolumn'] = df['db_table'] + '_1::' + df['col_name']
            for index, row in df.iterrows():
                formulas['expr'] = formulas['expr'].str.replace(row['col_name'], row['tablecolumn'])
        except: pass

        try:
            connectionobjsrels = connectionobjects.merge(relationships, on='tableobject', validate='1:m')
        except: pass
        try:
            connectionobjectsrelationships = connectionobjsrels.merge(destinationtables, on='destination', validate='m:1')
        except: pass
        try:
            connectionobjectsrelationships['on']='[' + connectionobjectsrelationships['name']+ '::' + connectionobjectsrelationships['lkey'] + '] ' + connectionobjectsrelationships['op'] + ' [' + connectionobjectsrelationships['destination']+ '::' + connectionobjectsrelationships['rkey'] + ']'   
        except: pass
        connectionstablesmetadata['file_name']=filename
        connectionstablesmetadata['fileid']= fileid
        connectionstablesmetadata.to_csv('./input/metadata_objects/metadata_{}.csv'.format(filename),index=False )
        
        try:
            connectionobjectsrelationships['filename']=filename
            connectionobjectsrelationships['fileid']= fileid
            connectionobjectsrelationships.to_csv('./input/relationships/relations_{}.csv'.format(filename),index=False )
        except: output_message('There are no relationships for ' + filename, "error")
        try:
            data = connectionobjectsrelationships
            data['join_path'] = data['name'] + '_' + data['destinationname']
            rel = data[['name','destinationname','join_path']]
            par = data[['name','destinationname','join_path']]
            df = rel.merge(par, how='right', left_on='destinationname', right_on='name')
            df2 = df.merge(rel, how='right', left_on='destinationname_y', right_on='name')
            df3 = df2[['destinationname','join_path_x','join_path_y','join_path']]
            df_unpivoted = df3.melt(id_vars=['destinationname'], var_name='paths', value_name='path_values')
            df_unpivoted.dropna(inplace=True)
            join_paths = df_unpivoted[['destinationname','path_values']] 
            join_paths.to_csv('./input/join_paths/path_{}.csv'.format(filename),index=False)
        except: output_message('There are no join paths for ' + filename, "error")        
        try: 
            formulas['filename']=filename
            formulas['fileid']= fileid
            formulas.to_csv('./input/formulas/formulas_{}.csv'.format(filename),index=False )
        except: output_message('There are no formulas for ' + filename, "error")

# Summary CSV output provided to list the various files that have been parsed        
        df = connectionstablesmetadata[["db_table","db","schema","connection","fileid"]].drop_duplicates()
        for index, row in df.iterrows():
            db_table = row['db_table']
            db = row['db']
            schema = row['schema']
            connection = row['connection']
            details = pd.DataFrame(columns=["filename", "filecount","fileid","db_table","db","schema","connection"])
            new_details = pd.DataFrame({"filename": [filename], "filecount": [filecount], "fileid": [fileid], "db_table": [db_table], "db": [db], "schema": [schema], "connection": [connection]})
            details = pd.concat([details, new_details], ignore_index=True)