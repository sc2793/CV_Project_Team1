import labelbox as lb
import argparse
import requests
import ndjson
import cv2

class ExportLabel(object):
    def __init__(self, api_key, project_id):
        self.api_key = api_key
        self.project_id = project_id

    def pull_datarows(self):
        '''
        //takes in a string project_id, and a string api_key
        //returns a list of [datarows] where each row, corresponds to a video and its annotation information in the labelbox format
        '''
        print("pulling data rows..")
        self.client = lb.Client(api_key=self.api_key)
        self.project = self.client.get_project(self.project_id)
        export_url = self.project.export_labels()
        labels = requests.get(export_url).json()
        print("labels exported: ", len(labels))
        datarows = []
        vid_id = 0
        for label in labels:
            datarow = {"vid_id": vid_id}
            annotation_url = label["Label"]["frames"]
            headers = {"Authorization": f"Bearer {self.api_key}"}
            annotations = ndjson.loads(requests.get(annotation_url, headers=headers).text)
            datarow["Datarow_ID"] = label["DataRow ID"]
            datarow["annotations"] = annotations
            datarow["video_url"] = label["Labeled Data"]
            datarows.append(datarow)
            vid_id+=1
        return datarows

    def pull_frames(self, video_link):
        '''
        //takes in a video link and returns a list of images as numpy arrays
        //return a list containing [-1] if the video failed to be pulled
        '''
        print("pulling frames..")
        vidcap = cv2.VideoCapture(video_link)
        success, image = vidcap.read()
        images = []
        while success:
            images.append(image)
            success, image = vidcap.read()
        return images if len(images)>0 else [-1]


    def build_class_dict(self, annotations):
        '''
        input:  [annotations]
        takes in a list of annotations, where each annotation is a dictionary object
        returns a dictionary that includes <key:featureId, value:classification> for every featureId in the "annotations" object
        '''
        print("building class dict..")
        class_dict = {}
        for annotation in annotations:
            for a_object in annotation["objects"]:
                feature_id = a_object["featureId"]
                classes = a_object["classifications"]
                if len(classes)==0:
                    class_dict[feature_id] = "car"
                else:
                    class_dict[feature_id] = classes[0]["answer"]["value"]
        return class_dict

    def build_yolo_annotations(self, datarow, class_dict):
        '''
        input: [annotations], {class_dict<featureId,classification>}
        takes in a list of annotations and a dictionary
        returns a list of tuples where each tuple is < Datarow_ID , yolo_label_string >
        '''
        print("build yolo annotations..")
        yolo_annotations = []
        datarow_id = datarow["Datarow_ID"]
        annotations = datarow["annotations"]
        for annotation in annotations:
            frame_number = annotation["frameNumber"]
            yolo_label_string = ""
            for a_object in annotation["objects"]:
                feature_id = a_object["featureId"]
                classification_number = 1 # refer to some dictionary using feature id's value
                bbox = a_object["bbox"]
                yolo_label_string += str(classification_number)+ " " + str(bbox["top"]) + " " + str(bbox["left"]) + " " + str(bbox["width"]) + " " + str(bbox["height"])
                yolo_label_string += "\n"
            yolo_annotations.append((str(datarow_id)+"_"+str(frame_number), yolo_label_string))
        return yolo_annotations

    def run(self):
        print("Let's make some yolo labels")
        datarows = self.pull_datarows()
        print("datarows:", len(datarows))
        for datarow in datarows:
            class_dict = self.build_class_dict(datarow["annotations"])
            yolo_annotations = self.build_yolo_annotations(datarow, class_dict)
            images = self.pull_frames(datarow["video_url"])
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="export_labels.py")
    parser.add_argument("--api-key")
    parser.add_argument("--project-id")
    opt = parser.parse_args()
    u = ExportLabel(opt.api_key, project_id=opt.project_id)
    u.run()