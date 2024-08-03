import sys
import os
import json
import csv
import pandas as pd
from utils.file_utils import list_folder, list_files_with_extension
from path_config import ROOT_PATH

FLAKY_BUILD_DIR = ROOT_PATH + '/possible-flaky-repos'
SUMMARY_DIR = '/unique-build-errors'
SUMMARY_FILE_IDENTIFIER = 'llm-summary-'
UNKNOWN = 'CORRUPTED_JSON_FORMAT'

LABELS_OUTPUT_FILE = ROOT_PATH + '/error_categorization/data/1-labels-2023.csv'
REPO_INFO_OUTPUT_FILE = ROOT_PATH + '/error_categorization/data/1-repo-info-2023.csv'

def get_repo_info(repo_path):
    labels_info = {
        'projects': [],
        'label': [],
        'cluster': [],
        'summaries': [],
    }
    
    repo_name = repo_path.split('/')[-1]
    summary_path = repo_path + SUMMARY_DIR
    summary_files = list_files_with_extension(summary_path, SUMMARY_FILE_IDENTIFIER)
    
    for summary_file in summary_files:
        build_date = summary_file.split('/')[-1].split(SUMMARY_FILE_IDENTIFIER)[-1].replace('.log.json', '')
        with open(summary_file, 'r') as f:
            try:
                data = json.load(f)
                
                # Depends on the format of the summary file, you may need to comment this line
                # data = json.loads(json.loads(data))
                
                label = data.get('label', UNKNOWN)
                cluster = data.get('initial cluster name', UNKNOWN)
                summary = data.get('summary', UNKNOWN)
                error_sources = data.get('sources of error', UNKNOWN)
                
                new_label = {
                    'projects': repo_name + '-' + build_date,
                    'label': label,
                    'cluster': cluster,
                    'summaries': f"PROJECT: {repo_name + '-' + build_date} \n\nLABEL: {label} \n\nSUMMARY: {summary} \n\nSOURCES: {error_sources}"
                }
                
            except:
                new_label = {
                    'projects': repo_name + '-' + build_date,
                    'label': label,
                    'cluster': 'UNKNOWN',
                    'summaries': UNKNOWN,
                }
                print(f"Error in reading summary file: {summary_file}")
            
            labels_info.update((key, labels_info[key] + [new_label[key]]) for key in labels_info)
            
    return labels_info

def update_cluster_info(labels_info, new_labels):
    for i, (project, summary, cluster) in enumerate(zip(new_labels['projects'], new_labels['summaries'], new_labels['cluster'])):
        index = -1 # Index of the cluster in the labels_info, if it's new, it will be -1 (to point to the last element of the list)
        
        summary_keys = [key for key in labels_info.keys() if key.startswith('summary-')]
        
        if cluster in labels_info['cluster']:
            index = labels_info['cluster'].index(cluster)
            labels_info['projects'][index].append(project)
            labels_info['num_of_projects'][index] += 1

        else:
            labels_info['cluster'].append(cluster)
            labels_info['projects'].append([project])
            labels_info['num_of_projects'].append(1)
            labels_info['parent_label'].append('')
            
            for summary_key in summary_keys: # Add empty cells for summaries (rows) in the new cluster
                labels_info[summary_key].append('')
        
        
        summary_len = len(summary_keys)
        found_empty_cell = False
        
        for summary_key in summary_keys: # fill the empty cell for the current index within the summary columns
            if labels_info[summary_key][index] == '':
                found_empty_cell = True
                labels_info[summary_key][index] = summary
                break
            
        if not found_empty_cell: # if all summaries (up to summary-n) if filled, add a new summary (column) for all the clusters (rows)
            labels_info[f'summary-{summary_len+1}'] = [''] * len(labels_info['cluster'])
            labels_info[f'summary-{summary_len+1}'][index] = summary
    
def extract_labels():
    labels_info = {
        'projects': [],
        'num_of_projects': [],
        'cluster': [],
        'parent_label': []
    }
    
    project_repos = list_folder(FLAKY_BUILD_DIR, True)
    for repo in project_repos:
        new_labels = get_repo_info(repo)
        update_cluster_info(labels_info, new_labels)
    
    return labels_info

def save_labels(labels):
    
    key_to_sort = 'num_of_projects'

    fieldnames = list(labels.keys())
    
    with open(LABELS_OUTPUT_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(fieldnames)

        for row in zip(*labels.values()):
            writer.writerow(row)

    # Sorting
    df = pd.read_csv(LABELS_OUTPUT_FILE)
    sorted_df = df.sort_values(key_to_sort, ascending=False)
    sorted_df.to_csv(LABELS_OUTPUT_FILE, index=False)


def extract_repo_info():
    repo_info = {
        'projects': [],
        'label': [],
        'cluster': [],
    }
    
    project_repos = list_folder(FLAKY_BUILD_DIR, True)
    for repo in project_repos:
        new_labels = get_repo_info(repo)
        repo_info.update((key, repo_info[key] + new_labels[key]) for key in repo_info)
        # update_cluster_info(repo_info, new_labels)
    
    repo_info['old_label'] = repo_info.pop('label')
    repo_info['old_cluster'] = repo_info.pop('cluster')
    print(repo_info)
    
    return repo_info

    
def save_repo_info(repo_info):
    fieldnames = list(repo_info.keys())
    
    with open(REPO_INFO_OUTPUT_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(fieldnames)

        for row in zip(*repo_info.values()):
            writer.writerow(row)

    # Sorting
    df = pd.read_csv(REPO_INFO_OUTPUT_FILE)
    sorted_df = df.sort_values('projects', ascending=True)
    sorted_df.to_csv(REPO_INFO_OUTPUT_FILE, index=False)
    
if __name__ == '__main__':
    # csv file for manual analysis
    # labels = extract_labels()
    # save_labels(labels)
    
    # csv file for comparing old and new labels for each repo
    repo_info = extract_repo_info()
    save_repo_info(repo_info)