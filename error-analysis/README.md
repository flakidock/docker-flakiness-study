# Error Analysis

## Error Categorization

To see error categorization functions, see `error_categorization` folder.

### dataset folder

-   `dataset`: Includes the following files. In order to get these files, you need to run `extract_zip_files.sh`:

```
repo_flaky_dataset.json: info dataset for flaky repos
repo_non_flaky_dataset.json: info dataset for non-flaky repos
```

Further details about these json files are mentioned [here](error_categorization/dataset_generation/README.md).

## Error Repair

### Requirements

1. To start the error repair procedure, first, make sure all the configs mentioned [here](../README.md) is properly set.
2. Make sure the folder `possible-flaky-repos` is extracted and contains only project folders (without compressed files).
3. Have `repositories` directory in the parent of the current project. The folder structure should be as follows: (each repo_name denotes the name of cloned project):

```log
<parent_directory>/
├── repositories/
│   ├── part1-1k/
│   │   └── repo_name1/
│   │   └── repo_name2/
│   │   └── ...
│   ├── part2-1k/
│   │   └── repo_name1/
│   │   └── repo_name2/
│   │   └── ...
│   ├── part3-1k/
│   │   └── repo_name1/
│   │   └── repo_name2/
│   │   └── ...
│   └── ...
└── <current_project>/
```
4. Make sure you've successfully unzipped the `possible-flaky-repos` as explained [here](../dataset/flake4dock/README.md).
5. Make sure you've successfully unzipped the json files inside `error-analysis/dataset`.

### Run FlakiDock with LLM & RAG

```bash
python error_repair/flakiDock/main.py
```

The output will be stored in the `<parent_directory>` under the folder name: `FlakiDock_output`.

### Run LLM with Dockerfile and Build output info

```bash
python error_repair/flakiDock/main_docker_and_build.py
```

The output will be stored in the `<parent_directory>` under the folder name: `FlakiDock_output_SD`.

### Run LLM with Dockerfile info

```bash
python error_repair/flakiDock/main_docker_only.py
```

The output will be stored in the `<parent_directory>` under the folder name: `FlakiDock_output_S`.

### Run PARFUM Dockerfile info

```bash
python error_repair/flakiDock/main_parfum.py
```

The output will be stored in the `<parent_directory>` under the folder name: `FlakiDock_output_S_PARFUM`.
