from path_config import ROOT_PATH, DATASET_PATH


# related to possible-flaky-repos
FLAKY_BUILD_DIR = ROOT_PATH + '/possible-flaky-repos'
NON_FLAKY_BUILD_DIR = ROOT_PATH + '/non-flaky-repos'


# related to summary files
SUMMARY_DIR = '/unique-build-errors'
SUMMARY_FILE_IDENTIFIER = 'llm-summary-'


# related to error-categorization labels
CATEGORY_HIERARCHY_FILE = ROOT_PATH + "/error_categorization/data/3-category-hierarchy/full-hierarchy.json"
FINAL_LABELS_FILE = ROOT_PATH + "/error_categorization/data/2-labels-2023-final.csv"
# dataset files needed for next steps: detection, repair, and evaluation
FLAKY_HISTORY_DATASET_FILE = DATASET_PATH + "/repo_flaky_history_dataset.json"
NON_FLAKY_BUILD_DATASET_FILE = DATASET_PATH + "/repo_non_flaky_dataset2.json"
FLAKY_BUILD_DATASET_FILE = DATASET_PATH + "/repo_flaky_dataset2.json"


# related to build outputs
BUILD_OUTPUTS_DIR = ROOT_PATH + '/raw_build_logs'


# related to final-label(csv) file keywords
SUMMARY_HEADER = 'summary-1'
PROJECT_TAG = 'PROJECT: '
CLUSTER_COLUMN_NAME = 'New (cluster)'


# related to category labels
TOP_CATEGORY = 'TOP_CATEGORY'
FINAL_CATEGORY_KEY = 'category'
DOCKERFILE_INDEPENDENT_FLAKINESS = 'non-flaky'