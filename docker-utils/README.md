# Dockerfile Build

## Prerequisites

Before running `docker-utils/docker_build.py`, make sure the following set of instructions are satisfied:

-   Have `repositories` directory in the parent of the current project. The folder structure should be as follows: (each repo_name denotes the name of cloned project):

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

## Execution

To trigger dockerfile build procedure in your machines (we run on 5 different machines), use the command below (replace 1 with 2,3,4, or 5 based on the machine in which the command is executed):

**Note:** Before running this command, make sure to set the followings properly:

- `parent_directory` inside `configs/git_clone/general-config.yaml`.
- `path_prefix` inside `scripts/build_docker_images_1.sh`
- `step 5: Docker <username> and <password>` inside `scripts/cleanup_docker_env`. 

```
bash scripts/build_docker_images_1.sh
```
