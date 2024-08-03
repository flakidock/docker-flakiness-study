from path_config import ROOT_PATH, DATASET_PATH, PARENT_PATH

REPOSITORIES_FOLDER = PARENT_PATH + "/repositories/"

STATIC_PARAMS = "dockerfile"
DYNAMIC_PARAMS = "metadata:error_segment"

EXCLUDED_CATEGORIES = "Off-Topic Errors"
MISCELLANEOUS_CATEGORY = "Miscellaneous Errors"
DOCKERFILE_INDEPENDENT_FLAKINESS = "Dockerfile-Independent Errors"
DOCKERFILE_DEPENDENCT_FLAKINESS = "Dockerfile-Related Errors"
CATEGORY_SEPARATOR = "->"

FLAKINESS_DATASET_PATH = DATASET_PATH + "/repo_flaky_dataset.json"
NON_FLAKINESS_DATASET_PATH = DATASET_PATH + "/repo_non_flaky_dataset.json"

REPAIRED_PROJECTS_PATH = ROOT_PATH + "/error_repair/data/repaired_projects.txt"
TEST_PROJECTS_PATH = ROOT_PATH + "/error_repair/data/test_projects.txt"
FLAKY_REPOS_PATH = ROOT_PATH + "/possible-flaky-repos/"
REPAIR_RECORD_PATH = ROOT_PATH + "/error_repair/data/repair_records.csv"

BUILD_SEGMENT_EMBEDDINGS_PATH = ROOT_PATH + "/error_repair/data/build_embeddings_truncated-ada2.pkl"
DEMONSTRATION_SEGMENT_EMBEDDINGS_PATH = ROOT_PATH + "/error_repair/data/demonstration_embeddings.pkl"
DEMONSTRATION_BUILD_SEGMENT_EMBEDDINGS_PATH = ROOT_PATH + "/error_repair/data/demonstration_build_embeddings.pkl"

FLAKIDOCK_BUILD_PATH = PARENT_PATH + "/FlakiDock_output/"
FLAKIDOCK_BUILD_PATH_LLAMA3_1 = PARENT_PATH + "/FlakiDock_output_LLAMA3_1/"
FLAKIDOCK_BUILD_PATH_SD = PARENT_PATH + "/FlakiDock_output_SD/"
FLAKIDOCK_BUILD_PATH_SD_LLAMA3_1 = PARENT_PATH + "/FlakiDock_output_SD_LLAMA3_1/"
FLAKIDOCK_BUILD_PATH_S = PARENT_PATH + "/FlakiDock_output_S/"
FLAKIDOCK_BUILD_PATH_S_LLAMA3_1 = PARENT_PATH + "/FlakiDock_output_S_LLAMA3_1/"
FLAKIDOCK_BUILD_PATH_S_PARFUM = PARENT_PATH + "/FlakiDock_output_S_PARFUM/"


STRUCTURE_ERROR = "STRUCTURE_ERROR"

REPAIRED_DOCKERFILES_PATH = ROOT_PATH + "/error_repair/flakiDock/parfum_repaired_dockerfiles/"

TEST_PERCENTAGE = 0.2

ROOT_CAUSE_SEPARATOR = "__________"

