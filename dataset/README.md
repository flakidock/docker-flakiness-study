This folder contains the following data:
- `Shipwright`: The initial shipwright dataset including ~20k Docker projects.
- `init_build_results`: The result of the first round, for setting the candidate Docker projects for temporal study.
- `flake4dock`: the dataset containing 8,132 non-flaky and flaky Dockerfiles. all the Dockerfiles come with their history of builds. For flaky Dockerfiles we also have their failures, and flakiness category. For 100 Flaky Dockerfiles, we also provide repairs. 
- `flakidock_results`: the results of flakidock and existing tools (Parfum).

Read [examples](examples.md) for some instances of different categories of flakiness and the effectiveness of FlakiDock.
