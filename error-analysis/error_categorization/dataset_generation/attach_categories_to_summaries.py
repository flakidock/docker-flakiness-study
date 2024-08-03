import json
from tqdm import tqdm
import csv
from error_categorization.dataset_generation.constants import FLAKY_BUILD_DIR, SUMMARY_DIR, SUMMARY_FILE_IDENTIFIER, CATEGORY_HIERARCHY_FILE, FINAL_LABELS_FILE, SUMMARY_HEADER, PROJECT_TAG, CLUSTER_COLUMN_NAME, TOP_CATEGORY, FINAL_CATEGORY_KEY
from utils.file_utils import read_file, list_files_with_extension, list_files, list_folder, remove_and_generate_new_dir


def get_category_string_from_hierarchy(category_hierarchy, current_category):
    category_hierarchy_list = []
    while current_category != TOP_CATEGORY:
        category_hierarchy_list.insert(0, current_category)
        current_category = category_hierarchy[current_category]

    return ' -> '.join(category_hierarchy_list)


def update_summary_files(category_hierarchy, project_labels, list_of_repos):
    for repo_dir in tqdm(list_of_repos):
        summary_path = repo_dir + SUMMARY_DIR
        summary_files = list_files_with_extension(
            summary_path, SUMMARY_FILE_IDENTIFIER)

        project_name = repo_dir.split('/')[-1]
        build_dates = [summary_file.split('/')[-1].split(SUMMARY_FILE_IDENTIFIER)[-1].replace(
            '.log.json', '') for summary_file in summary_files]

        try:
            project_ids = [project_name + '-' +
                           build_date for build_date in build_dates]
            categories = []
            for project_id in project_ids:
                categories.append(get_category_string_from_hierarchy(
                    category_hierarchy, project_labels[project_id]))
        except Exception as e:
            print(f"Error in finding projects ids: {e}")

        for summary_file, category in zip(summary_files, categories):
            try:
                with open(summary_file, 'r') as f:
                    data = json.load(f)

                data[FINAL_CATEGORY_KEY] = category

                with open(summary_file, 'w') as f:
                    f.write(json.dumps(data, indent=4))

            except Exception as e:  # This exception should not happen!
                print(
                    f"Error reading {summary_file}: {e}: category {category}")


def get_category_hierarchy(file_path):
    category_hierarchy = {}

    with open(file_path, 'r') as f:
        data = json.load(f)
    categories = data[list(data.keys())[0]]

    for category in categories:
        category_hierarchy[category] = TOP_CATEGORY

        for subcategory in categories[category]:
            category_hierarchy[subcategory] = category

            for subsubcategory in categories[category][subcategory]:
                category_hierarchy[subsubcategory] = subcategory

                if isinstance(categories[category][subcategory], dict):
                    for subsubsubcategory in categories[category][subcategory][subsubcategory]:
                        category_hierarchy[subsubsubcategory] = subsubcategory

    return category_hierarchy


def get_project_labels(file_path):
    project_labels = {}

    # Open the CSV file
    with open(file_path, newline='') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Iterate over each row in the CSV file

        summary_start_index = 0
        cluster_column_index = 0
        for i, row in enumerate(csv_reader):
            if i == 0:  # the first row: headers
                for j, item in enumerate(row):  # iterate over the headers
                    if item == CLUSTER_COLUMN_NAME:
                        cluster_column_index = j
                    elif item == SUMMARY_HEADER:
                        summary_start_index = j

            # read cells containing summaries metadata
            for item in row[summary_start_index:]:
                context_lines = item.split('\n')

                for line in context_lines:
                    if PROJECT_TAG in line:
                        project = line.split(PROJECT_TAG)[-1].strip()
                        project_labels[project] = row[cluster_column_index]

    return project_labels


# purpose: update the summary files and append the category name (finalized)
if __name__ == '__main__':
    list_of_repos = list_folder(FLAKY_BUILD_DIR, False)

    # get category hierarchy: TOP_CATEGORY -> category -> subcategory -> subsubcategory -> subsubsubcategory
    category_hierarchy = get_category_hierarchy(CATEGORY_HIERARCHY_FILE)

    # get project labels: project -> subsubcategory OR subsubsubcategory
    project_labels = get_project_labels(FINAL_LABELS_FILE)

    # update the summary files with the final category name
    update_summary_files(category_hierarchy, project_labels, list_of_repos)
