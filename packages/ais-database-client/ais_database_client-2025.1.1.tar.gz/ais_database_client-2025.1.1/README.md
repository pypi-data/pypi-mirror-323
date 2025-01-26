# AIS Database Client

Python client for the [Space Eye AIS server](). The AIS server aggregates data from AIS receives and the [UN Task Team in AIS data analyses](https://unstats.un.org/bigdata/task-teams/ais/index.cshtml).

# License

This project is [Apache 2.0](LICENSE.txt) licensed.


### Deployment to Pypi
1. Install Dependencies if you haven't already:

```
pip install .
```

2. Build the Package:

Run the following command to build your package (Install build if you haven't already):
``` 
python -m build
```
3. Upload to PyPI:

Upload your package to PyPI:
```
twine upload dist/*
```