# GHALogs: Large-scale dataset of GitHub Actions runs

This code repository contains code and link to dataset presented in the paper "GHALogs: Large-scale dataset of GitHub Actions runs".


## Dataset

Dataset is not hosted in the Git repository because of its large size (~140GB).  
It is hosted on Zenodo: <https://doi.org/10.5281/zenodo.10154920> 

:warning: File sizes  
`repositories.json.gz` and `runs.json.gz` are ~1GB in total, but `github_run_logs.zip` is about 142GB!  
Logs archive is **not** required to run Jupyter notebooks and explore runs metadata!  
However, logs are required to run the log parsing again (e.g., extract commands used in runs)

ℹ️ An example of the data available in the dataset with the same format (repository info, run info, run logs) can be found in the `examples` folder within this repository.

## Notebooks

Jupyter notebooks are stored in the `jupyter` folder in this code repository.
They expect a MongoDB database to be run seamlessly.

### Prerequisites

Notebooks expect a MongoDB database.

1. MongoDB database

If you don't have a MongoDB database, you can use Docker to quickly start a MongoDB database.  
Below a command to start a container based on the mongo image.  
Note: All data will be lost when container exits!

```sh
docker run -it --rm -p 127.0.0.1:27017:27017 --name gha-mongodb mongo:7
```

See the [documentation](https://hub.docker.com/_/mongo) for more information on deploying MongoDB for production (e.g., persistence).

2. Import data in MongoDB.

Data for MongoDB is stored as gzip JSON lines (e.g., enable users to access data without MongoDB).  
However, Jupyter notebooks expect a MongoDB database to run queries.

a. Download `repositories.json.gz` and `runs.json.gz` (see Section Dataset above)  
b. Run cells in the notebook `0 - Load data`.

### Reproduce results

Notebook `1 - Dataset metrics` allow you to reproduce the results presented in the paper.
Each step of the notebooks is documented inside the notebook.

Enjoy your discovery!


## Github Actions runs scraper

Code used to retrieve Github Actions runs is stored in this repository.
More info to come!
