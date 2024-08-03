#for every file in original_dockerfiles, run the following command:
# docker-parfum repair --stdin original_dockerfiles/<file_name> -o repaired_dockerfiles/<file_name>

import os
import subprocess

original_dockerfiles = os.listdir('original_dockerfiles')
for file in original_dockerfiles:
    command = f'docker-parfum repair --stdin original_dockerfiles/{file} -o repaired_dockerfiles/{file}'
    subprocess.run(command, shell=True)
    print(f'{file} repaired')