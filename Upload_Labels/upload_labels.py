import labelbox as lb
import labelbox.types as lb_types
import uuid
from test_label import sample_label

class UploadLabel(object):
    def __init__(self):
        print("initialised")
        API_KEY=""
        self.client = lb.Client(api_key=API_KEY)
        # self.ontology = client.get_ontology("clevph27n2o060723bkfw16r4")
        self.global_key = ""
        self.project = self.client.get_project("")
        # self.project.setup_editor(self.ontology)

    def upload_video(self):
        client = self.client
        self.global_key = "2118--41.mp4"
        asset = {
            "row_data": "/Users/rachanachaudhari/Projects/CV-project-Team-2/UploadLabels/2118--41.mp4", 
            "global_key": self.global_key,
            "media_type": "VIDEO"
        }

        dataset = client.create_dataset(name="video_demo_dataset")
        task = dataset.create_data_rows([asset])
        task.wait_till_done()
        print("Errors :",task.errors)
        print("Failed data rows:", task.failed_data_rows)   

    def upload_batch_videos(self):
        project = self.project
        # # Create a batch to send to your MAL project
        batch = project.create_batch(
        "first-batch-video-demo1", # Each batch in a project must have a unique name
        global_keys=[self.global_key], # A paginated collection of data row objects, a list of data rows or global keys
        priority=5 # priority between 1(Highest) - 5(lowest)
        )

        print("Batch: ", batch)

    def upload_label(self):
        upload_job_label_import = lb.LabelImport.create_from_objects(
            client = self.client,
            project_id = self.project.uid, 
            name = "label_import_job-" + str(uuid.uuid4()),
            labels=[sample_label]
            )

        upload_job_label_import.wait_until_done()
        print("Errors:", upload_job_label_import.errors)
        print("Status of uploads: ", upload_job_label_import.statuses)
        print("   ")
            
    def run(self):
        # self.upload_video()
        self.upload_label()

if __name__ == '__main__':
    u = UploadLabel()
    u.run()