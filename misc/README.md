# Misc folder

- `get_github_repo.py`: Get repositories list from <seart-ghs.si.usi.ch> and store them in a JSON lines file
- `shuffle_repositories.py`: Shuffle list of repositories stored in JSON lines (so a partial scraping should be representative)
- `get_github_workflow_runs.py`: From list of repositories, identify repositories and runs that follow defined criterions and store them in a SQLite3 database.
