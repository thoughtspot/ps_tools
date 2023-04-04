from typing import Any
import datetime as dt
import logging
import pathlib
import pandas as pd
import toml
import typer
import pytz
import os
from ._util import State
from ._ux import comment, console, output_message
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
import json
from tableau_tools._client import *
from tableau_tools._tabimport import *
#from ._snowflake import *
from rich.progress import track
from rich.table import Table as tbl
from rich.progress import Progress

path = os.getcwd()
par_path = os.path.abspath(os.path.join(path, os.pardir))

log = logging.getLogger(__name__)

app = typer.Typer(
    help="""tableau tools.""",
    add_completion=False,
    no_args_is_help=True,
    # global settings
    context_settings={
        "help_option_names": ["--help", "-h"],
        "obj": State(),  # safely carry around global state
        "max_content_width": console.width,  # allow responsive console design
        "show_default": False,
        "token_normalize_func": lambda x: x.casefold(),  # allow case-insensitive commands
    },
)

@ app.command(name="convert_files")
def convert_twb(
    ctx: typer.Context,
    #cfg_name: str = typer.Option(..., help="Name of config file")
):
    summary = pd.DataFrame(columns=["filename", "filecount","fileid"])
    details = pd.DataFrame(columns=["filename", "filecount","fileid","db_table","db","schema","connection"])
    filecount = 0
    for filetype in ['twb','tds']:
        directory = f'./input/{filetype}/'
        for filename in os.listdir(directory): #tableauxmls=default
            filecount += 1
            fileid = 'tdsid'+str(filecount)
            new_row = pd.DataFrame({"filename": [filename], "filecount": [filecount], "fileid": [fileid]})
            summary = pd.concat([summary, new_row], ignore_index=True)            
            parse_tableau(filename)
            console.print(f"check {filetype}: {filename}",style = 'success')
    console.print(f"check {summary}",style = 'success')
    summary.to_csv('./input/exportinfo/summary.csv',index=False )
        #details.to_csv('./input/exportinfo/details.csv',index=False )
"""
@ app.command(name="create_tables")
def create_tables(
    ctx: typer.Context,
    #cfg_name: str = typer.Option(..., help="Name of config file")
):
    cs = sf_connect()
    create_database('CUST','MY_WH','hyperfiles_db','default_schema')
    cs.close()
    ctx.close()
"""
@ app.command(name="create_spotapps")
def create_spotapps(
    ctx: typer.Context,
    type: str = typer.Option(..., help="type of files (twb/tds/hyper")
):
    #list_tds_files = ['SF Trial.tds']
    list_tds_files = os.listdir(f'./input/{type}/')
    for tds in list_tds_files:
        try:
            create_spotapp(tds)
            shutil.make_archive('./output/SpotApps/{}'.format(tds), 'zip', './output/TML/{}'.format(tds))
            output_message("successfully created SpotApp for {} ".format(tds), "success")
        except:
            output_message("failed to create SpotApp {} ".format(tds), "error")

def main():
    """
    Main entrypoint.
    """
    #_load_environment_defaults(context_settings=app.info.context_settings)

    try:
        app(prog_name="tableau_tools")
    except Exception as E:
        output_message("Whoopsie, something went wrong! Check log file for errors", "error")
        log.exception("whoopsie, something went wrong!")


if __name__ == "__main__":
    raise SystemExit(main())