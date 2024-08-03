import os
import subprocess

def stash_changes(repo_path):
    """
    Stashes changes in the given repository path.
    """
    try:
        # Navigate to the repository
        print(f"Navigating to {repo_path}")
        os.chdir(repo_path)

        # Check if the repository has unstaged changes
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            # Stash changes if there are any
            subprocess.run(['git', 'stash', '-u'])
            print(f"********** Changes stashed in {repo_path}")
        # else:
            # print(f"No changes to stash in {repo_path}")
    except Exception as e:
        print(f"Failed to stash changes in {repo_path}: {e}")
    finally:
        # Go back to the original directory: two layers up
        os.chdir("../../../")
        

def process_repositories(base_path):
    """
    Process each part folder in the base_path.
    """
    try:
        for part in os.listdir(base_path):
            part_path = os.path.join(base_path, part)
            if os.path.isdir(part_path) and part.startswith('part'):
                for repo in os.listdir(part_path):
                    repo_path = os.path.join(part_path, repo)
                    if os.path.isdir(repo_path):
                        stash_changes(repo_path)
    except Exception as e:
        print(f"Error processing repositories: {e}")

if __name__ == "__main__":
    base_path = 'repositories'  # Change this to your actual base path
    process_repositories(base_path)