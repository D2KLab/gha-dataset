# GHALogs: A Large-Scale Dataset of GitHub Actions Runs

This repository provides the dataset and artifacts associated with the paper _"GHALogs: A Large-Scale Dataset of GitHub Actions Runs"_, presented at the **[Mining Software Repositories 2025 (MSR'25)](https://2025.msrconf.org/)** conference.

The **GHALogs dataset** contains over **116,000 CI/CD workflows** executed via **GitHub Actions (GHA)**, collected from more than **25,000 public repositories** across **20 programming languages**. In total, the dataset includes **513,000 workflow runs** and approximately **2.3 million individual steps**, offering a rich foundation for research on CI/CD practices, failure analysis, software engineering automation, and more.

See the [examples](examples) folder for a quick overview of the data format.

If you use this dataset in your research, please cite our paper:

```bibtex
@inproceedings{msr25_ghalogs,
  author = {Moriconi, Florent and Durieux, Thomas and Falleri, Jean-Rémi and Francillon, Aurélien and Troncy, Raphael},
  title = {GHALogs: Large-Scale Dataset of GitHub Actions Runs},
  year = {2025},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  location = {Ottawa, Canada},
  series = {MSR '25}
}
```

## Paper

The paper is available [here](paper.pdf).

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
