from typing import NamedTuple

class ClusterItem:
    def __init__(self, embedding, info):
        self.embedding = embedding
        self.info = info
        
class DockerErrorTrace(NamedTuple):
    error_segment: str
    error_line: str
    dockerfile_segment: str
    exit_code: str
    
class SummaryInfo:
    def __init__(self, project, label, summary, sources):
        self.project = project
        self.label = label
        self.summary = summary
        self.sources = sources
    
    def serialize_object(self):
        return {
            'project': self.project,
            'label': self.label,
            'summary': self.summary,
            'sources': self.sources
        }
        
    def serialize_str(self):
        # f"Label: {self.label}\nSummary: {self.summary}\nSources: {self.sources}"
        return self.label
    
    def serialize_full_str(self):
        return f"Project: {self.project}\nLabel: {self.label}\nSummary: {self.summary}\nSources: {self.sources}"

class DockerfileExecutionRecord:
    def __init__(self, error_line, category, top_category, error_segment, dockerfile_segment, build_output, build_time):
        self.error_line = error_line
        self.category = category
        self.top_category = top_category
        self.error_segment = error_segment
        self.dockerfile_segment = dockerfile_segment
        self.build_output = build_output
        self.build_time = build_time
    
    def __str__(self) -> str:
        return f"\tError Line: {self.error_line}\n\tCategory: {self.category}\n\tTop Category: {self.top_category}"
    

class DockerfileFlakinessInfo:        
    def __init__(self, project_name, dockerfile, is_flaky, build_output=""):
        self.project_name = project_name
        self.dockerfile = dockerfile
        self.is_flaky = is_flaky
        self.records = []
        self.build_output = build_output
        
    def __str__(self) -> str:
        serialized_str = f"Dockerfile: {self.dockerfile}\nFlakiness: {self.is_flaky}\nRecords:"
        for record in self.records:
            serialized_str += f"\n[\n{str(record)}\n]"
        
        return serialized_str
    
    def get_error_lines(self):
        return [record.error_line for record in self.records if record.error_line != "unknown"]
    
    def get_categories(self):
        return [record.category for record in self.records]
    
    def get_top_categories(self):
        return [record.top_category for record in self.records]
    
    
class DemonstrationMetadata:
    def __init__(self, root_cause_info, error_line, error_category):
        self.root_cause_info = root_cause_info
        self.error_line = error_line
        self.top_category = error_category.split("->")[0].strip()
        self.sub_category = error_category.split("->")[1].strip()


class DemonstrationRecord:
    def __init__(self, dockerfile, build_output, root_cause_label, repair, rounds, metadata):
        self.dockerfile = dockerfile
        self.build_output = build_output
        self.root_cause_label = root_cause_label
        self.repair = repair
        self.rounds = rounds
        self.metadata = metadata
        
        
class FeedbackInfo:
    def __init__(self, dockerfile, build_output) -> None:
        self.dockerfile = dockerfile
        self.build_output = build_output