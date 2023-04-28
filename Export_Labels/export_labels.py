import labelbox as lb
import argparse
import requests
import ndjson
import cv2
import yaml
import altFile as af

class ExportLabel(object):
    def __init__(self, api_key, project_id, yaml_path, destination_path):
        self.api_key = api_key
        self.project_id = project_id
        self.destination_path = destination_path
        with open(yaml_path, 'r') as file:
            self.classification_ref = yaml.safe_load(file)

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

    def pull_frames(self, video_link, frame_exclusions=[]):
        '''
        //takes in a video link and returns a list of images as numpy arrays
        //return a list containing [-1] if the video failed to be pulled
        '''
        print("pulling frames..")
        vidcap = cv2.VideoCapture(video_link)
        success, image = vidcap.read()
        images = []
        frame_count = 1
        while success:
            if frame_count not in frame_exclusions:
                images.append(image)
            success, image = vidcap.read()
            frame_count += 1
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
                    class_dict[feature_id] = classes[0]["answer"]["value"].lower()
        return class_dict

    def build_yolo_annotations(self, datarow, class_dict):
        '''
        input: [annotations], {class_dict<featureId,classification>}
        takes in a list of annotations and a dictionary
        returns a list of tuples where each tuple is < Datarow_ID , yolo_label_string > and a list of frame numbers that
        did not have any annotations attached
        '''
        print("build yolo annotations..")
        yolo_annotations = []
        datarow_id = datarow["Datarow_ID"]
        annotations = datarow["annotations"]
        frame_exclusions = []
        frame_count = 1
        for annotation in annotations:
            frame_number = annotation["frameNumber"]
            if frame_number!=frame_count:
                frame_exclusions += [f for f in range(frame_count, frame_number)]
                frame_count = frame_number+1
            else:
                frame_count+=1
            yolo_label_string = ""
            for a_object in annotation["objects"]:
                feature_id = a_object["featureId"]
                classification_number = self.classification_ref["names"].index(class_dict[feature_id])
                bbox = a_object["bbox"]
                yolo_label_string += str(classification_number)+ " " + str(bbox["top"]) + " " + str(bbox["left"]) + " " + str(bbox["width"]) + " " + str(bbox["height"])
                yolo_label_string += "\n"
            yolo_annotations.append((str(datarow_id), yolo_label_string))
        return yolo_annotations, frame_exclusions

    def run(self):
        print("Let's make some yolo labels")
        af.make_directories(self.destination_path, "train", "test")
        datarows = self.pull_datarows()
        print("datarows:", len(datarows))
        # images = []
        # yolo_annotations = []
        for datarow in datarows:
            class_dict = self.build_class_dict(datarow["annotations"])
            yolo_annotations, frame_exclusions = self.build_yolo_annotations(datarow, class_dict)
            images = self.pull_frames(datarow["video_url"], frame_exclusions)
            print("images: ", len(images))
            permutations = af.make_permutations(len(images), [0, 1], [0.20, 0.80])
            images_paths = af.shuffle_dir([self.destination_path+"/images/test", self.destination_path+"/images/train"], permutations)
            label_paths = af.shuffle_dir([self.destination_path+"/labels/test", self.destination_path+"/labels/train"], permutations)
            # print(label_paths)
            af.write_yolo_annotations(label_paths, yolo_annotations)
            result = af.save_frames(images, images_paths, datarow["Datarow_ID"])
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="export_labels.py")
    parser.add_argument("--api-key")
    parser.add_argument("--project-id")
    parser.add_argument("--yaml-path")
    parser.add_argument("--destination-path")
    opt = parser.parse_args()
    u = ExportLabel(opt.api_key, opt.project_id, opt.yaml_path, opt.destination_path)
    u.run()