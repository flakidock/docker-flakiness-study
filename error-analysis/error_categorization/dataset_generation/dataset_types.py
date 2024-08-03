class RepoMetadata:
    def __init__(self, error_segment: str = "", error_summary: str = "", initial_category: str = "", dockerfile_error_line: str = "", dockerfile_error_segment: str = "", dockerfile_exit_code: str = "", stderr_line: str = "", sources_of_error: list = []):
        self.error_segment = error_segment
        self.error_summary = error_summary
        self.initial_category = initial_category
        self.dockerfile_error_line = dockerfile_error_line
        self.dockerfile_error_segment = dockerfile_error_segment
        self.dockerfile_exit_code = dockerfile_exit_code
        self.stderr_line = stderr_line
        self.sources_of_error = sources_of_error
        

class RepoInfo:
    def __init__(self, repo_name: str, build_time: str, dockerfile: str, build_output: str, category: str, metadata: RepoMetadata):
        self.repo_name = repo_name
        self.build_time = build_time
        self.dockerfile = dockerfile
        self.build_output = build_output
        self.category = category
        self.metadata = metadata

    def to_dict(self):
        return {
            'repo_name': self.repo_name,
            'build_time': self.build_time,
            'dockerfile': self.dockerfile,
            'build_output': self.build_output,
            'category': self.category,
            'metadata': self.metadata.__dict__
        }


class RepoHistory:
    def __init__(self, repo_name: str, build_history: dict):
        self.repo_name = repo_name
        self.build_history = build_history

    def to_dict(self):
        return {
            'repo_name': self.repo_name,
            'build_history': self.build_history
        }
