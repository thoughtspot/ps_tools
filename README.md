# tableau2ts
Steps:
1. Download zip and then unzip the file or pull from git 
2. Navigate to where the files are such as
cd documents/tab2ts/tab2ts
3. Deactivate conda if you have it
conda deactivate
4. Run below:
pip install -e .
pip install git+https://github.com/thoughtspot/thoughtspot_tml.git@build-spec
pip install "thoughtspot_tml @ https://github.com/thoughtspot/thoughtspot_tml/archive/v2.0.1.zip"
pip install thoughtspot_rest_api_v1
5. Run tableau_tools --help
6. Run tableau_tools convert_tds