class ProjectDetails:
    def __init__(self, repo_name, repo_directory, dockerfile_exists, dockerfile_path, index, shell_output, exec_command, input_dir, output_dir, part_number):
        self.repo_name = repo_name
        self.repo_directory = repo_directory
        self.dockerfile_exists = dockerfile_exists
        self.dockerfile_path = dockerfile_path
        self.index = index
        self.shell_output = shell_output
        self.exec_command = exec_command
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.part_number = part_number
