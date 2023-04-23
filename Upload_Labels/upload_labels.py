import labelbox as lb
import uuid
from test_label import sample_label
import argparse
import json

class UploadLabel(object):
    def __init__(self, api_key, labels, project_id, ontology_id=""):
        print("initialised")
        self.client = lb.Client(api_key=api_key)
        self.project = self.client.get_project(project_id)
        labels = json.load(labels)
        self.labels = labels if isinstance(labels, list) else [labels]
        # if you want to get an ontology
        # self.ontology = client.get_ontology(ontology_id)
        # self.project.setup_editor(self.ontology)

    def upload_video(self, global_key, row_data, dataset="video_demo_dataset"):
        client = self.client
        asset = {
            "row_data": row_data, 
            "global_key": global_key,
            "media_type": "VIDEO"
        }
        dataset = client.create_dataset(name=dataset)
        task = dataset.create_data_rows([asset])
        task.wait_till_done()
        print("Errors :",task.errors)
        print("Failed data rows:", task.failed_data_rows)   

    def upload_batch_videos(self, global_keys):
        project = self.project
        batch = project.create_batch(
            "first-batch-video-demo1", # Each batch in a project must have a unique name
            global_keys=global_keys, # A paginated collection of data row objects, a list of data rows or global keys
            priority=5 # priority between 1(Highest) - 5(lowest)
        )
        print("Batch: ", batch)

    def upload_labels(self):
        upload_job_label_import = lb.LabelImport.create_from_objects(
            client = self.client,
            project_id = self.project.uid, 
            name = "label_import_job-" + str(uuid.uuid4()),
            labels=self.labels
        )
        upload_job_label_import.wait_until_done()
        print("Errors:", upload_job_label_import.errors)
        print("Status of uploads: ", upload_job_label_import.statuses)

            
    def run(self):
        # self.upload_video(global_key="5023--41.mp4", row_data="/Users/rachanachaudhari/Projects/CV-project-Team-2/Test_Videos/5023--41.mp4")
        self.upload_labels()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="upload_labels.py")
    parser.add_argument("--api-key")
    parser.add_argument("--label-file", type=argparse.FileType('r'))
    parser.add_argument("--project-id")
    parser.add_argument("--ontology-id", default="")
    opt = parser.parse_args()
    u = UploadLabel(opt.api_key, opt.label_file, project_id=opt.project_id, ontology_id=opt.ontology_id)
    u.run()