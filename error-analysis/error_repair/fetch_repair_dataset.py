import os
from error_repair.constants import FLAKY_REPOS_PATH, REPAIRED_PROJECTS_PATH
from utils.file_utils import list_folder


if __name__ == "__main__":
    project_paths = list_folder(FLAKY_REPOS_PATH, False)
    
    # check if there is a file: root_cause.txt in the project path
    repaired_paths = []
    for project_path in project_paths:
        root_cause_file = os.path.join(project_path, 'root_cause.txt')
        if os.path.exists(root_cause_file):
            repaired_paths.append(project_path)
    
    repaired_projects = [repaired_path.split('/')[-1] for repaired_path in repaired_paths]
    print(f"Number of repaired projects: {len(repaired_projects)}")
    
    with open(REPAIRED_PROJECTS_PATH, 'w') as f:
        for project in repaired_projects:
            f.write(project + '\n')