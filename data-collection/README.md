# Data Collection

Initiate data collection (GitHub repositories) using a new screen (or `tmux`) is highly recommended:

```
screen -S part1_data_collection
```

How to interact with screens:

-   `Ctrl+a` `d` exit the screen.
-   `screen -ls` to see the list of screens.
-   `screen -r session_name` to join a screen.
-   `screen -X -S session_name kill` to kill a screen.
-   `killall screen` to kill all screens.

Inside a screen, collect data using config files provided in `config` directory. Config files read dataset from a .txt file stored in `dataset` directory (in batches of 1k repositories). For example, use the command below for the first batch:

**Note:** Before running this command, make sure `parent_directory` is properly set inside `configs/git_clone/general-config.yaml`.

```
python clone_git_repos.py -g ../configs/git_clone/general-config.yaml -c ../configs/git_clone/part1.yaml
```

**Note:** Currently we have 21 batches (shipwright dataset, 1k per each batch).
