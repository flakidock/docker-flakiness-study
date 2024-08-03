from git import Repo
from datetime import datetime

def fetch_last_commit_sha(repo_path, end_date):
    repo = Repo(repo_path)
    last_commit = list(repo.iter_commits(until=end_date, max_count=1))[0]
    return last_commit.hexsha