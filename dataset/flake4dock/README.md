Flake4Dock contains the following information:
- `compressed_data`: This folder contains the category hierarchies and projects information, in a compressed form.
- `non-flaky-repos`: This directory includes the obvious non flaky Dockerfiles without failures during our study timeframe.
- `possible-flaky-repos`: This folder includes Dockerfiles with at least 1 failure during our study. These failures can happend due the following reasons:
    - <mark>Flakiness of the Dockerfile</mark>.
    - Dockerhub temporary issues.
    - Infrastructure issues.
    - Project specific issues.


We only consider the first item as `Dockerfile Flakiness`.

 **Note:** 100 of the flaky Dockerfiles inside `possible-flaky-repos` come with `repair` and `modification` (patch file).
 - If only one repair is provided:
    - `repair.Dockerfile` & `modification.Dockerfile`
- If more than one repair is provided:
    - `repair1.Dockerfile` & `modification1.Dockerfile`
    - `repair2.Dockerfile` & `modification2.Dockerfile`
    - ...


## Unzipping
You need a minimum of 5GB for unzipping possible-flaky-repos and a minimum of 20GB for non-flaky-repos.

simply run:

```bash
python unzip_files.py -i possible-flaky-repos\(zipped\) -o possible-flaky-repos ../../error-analysis/possible-flaky-repos
```
and,

```bash
python unzip_files.py -i non-flaky-repos\(zipped\) -o non-flaky-repos
```
