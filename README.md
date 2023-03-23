![Logo](ThoughtSpot_logo_2019.png)
<div align="center">
  <h2><b>Tableau to Thoughtspot</b></h2>
  <img src="ThoughtSpot_logo_2019.png" />
  <i>a Command Line Tool to convert tableau data source objects to </i> <b>ThoughtSpot</b> <i>Modeling Language (TML) files programmatically</i>

  <h3>
    <a href="#installation">🛠 Installation</a>
    <span> | </span>
    <a href="#features">📎 Features</a>
    <span> | </span>
    <a href="#migration-to-v200">🚨 Troubleshooting</a>
    <span> | </span>
    <a href="#reference">Reference</a>
    <span> | </span>
    <a href="#notes-on-thoughtspot-modeling-language">📝 Notes</a>
  </h3>

🚨 __The tools are built on[thougthspot_tml v2.0.0](#migration-to-v200)__. 🚨
</div>

*This package will not perform validation of the constructed TML files or interact with your* __ThoughtSpot__ *cluster!*


## Installation

`tableau_tools` requires at least __Python 3.7__, *preferably* __Python 3.9__ and above.

__Installation is as simple as:__
```shell
#Download the zip file from Github
#Create a virtual environment
python -m venv ts2tab
source ts2tab/bin/activate
pip install -e . 
```

## Features

The following commands are available in the current beta version:

```python
# worksheet_remapping.py
from thoughtspot_tml import Worksheet
import argparse
import pathlib

```

```shell
>>> tableau_tools convert_files --help

usage: [--help] [-s SRC] [-d DST] convert_files

positional arguments:
  None         

options:
  -h, --help                show this help message and exit
  -s SRC, --src-prefix SRC  (default: DEV_)
  -d DST, --dst-prefix DST  (default: TEST_)
```


## Reference

## Notes
