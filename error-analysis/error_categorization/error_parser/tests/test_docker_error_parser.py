import unittest
from error_categorization.error_parser.docker_error_parser import get_error_segments_as_json
from utils.file_utils import read_file, list_files, list_files_with_extension
from path_config import ROOT_PATH

DEFAULT_FILE_NAME = 'test_docker_error_parser/log-2023-05-10-20.failure'
DEFAULT_DIRECTORY_NAME = ROOT_PATH + '/possible-flaky-repos/'
UNKNOWN = "unknown"


class TestDockerErrorParser(unittest.TestCase):
    def test_get_error_segments_as_json(self):
        path = DEFAULT_FILE_NAME
        raw_build_log = read_file(path)
        build_info = get_error_segments_as_json(path, raw_build_log)

        self.assertIsNotNone(build_info["file_name"])
        self.assertIsNotNone(build_info["error_segment"])
        self.assertIsNotNone(build_info["dockerfile_error_line"])
        self.assertIsNotNone(build_info["stderr"])

        self.assertIsInstance(build_info["file_name"], str)
        self.assertIsInstance(build_info["error_segment"], str)
        self.assertIsInstance(build_info["dockerfile_error_line"], str)
        self.assertIsInstance(build_info["stderr"], str)

    # """
    # Given a directory of all docker build logs
    # When I run the docker error parser
    # Then I should get a get_error_segments_as_json where each entry is a valid entry 
    # """
    # def test_all_builds_from_a_directpry(self):
    #     directory = DEFAULT_DIRECTORY_NAME
    #     list_of_files = list_files_with_extension(directory, extension="failure.log")

    #     for path in list_of_files:
    #         raw_build_log = read_file(path)
    #         build_info = get_error_segments_as_json(path, raw_build_log)

    #         self.assertIsNotNone(build_info["file_name"])
    #         self.assertIsNotNone(build_info["error_segment"])
    #         self.assertIsNotNone(build_info["dockerfile_error_line"])
    #         self.assertIsNotNone(build_info["stderr"])

    """
    Given a directory of all docker build logs
    When I run the docker error parser
    Then I should get a get_error_segments_as_json where each entry is a valid entry and not "unknown"
    """
    def entry_should_not_be_unknown(self):
        directory = DEFAULT_DIRECTORY_NAME
        list_of_files = list_files_with_extension(directory, extension="failure.log")

        for path in list_of_files:
            raw_build_log = read_file(path)
            build_info = get_error_segments_as_json(path, raw_build_log)

            self.assertNotEqual(build_info["file_name"], UNKNOWN)
            self.assertNotEqual(build_info["error_segment"], UNKNOWN)
            self.assertNotEqual(build_info["dockerfile_error_line"], UNKNOWN)
            self.assertNotEqual(build_info["stderr"], UNKNOWN)

            self.assertIsInstance(build_info["file_name"], str)
            self.assertIsInstance(build_info["error_segment"], str)
            self.assertIsInstance(build_info["dockerfile_error_line"], str)
            self.assertIsInstance(build_info["stderr"], str)


if __name__ == '__main__':
    unittest.main()
