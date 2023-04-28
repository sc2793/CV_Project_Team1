import shutil, random, os, cv2

def make_directories(path, train_name = "train", test_name = "test"): 
#   take in a path, and creates the yolo directory structure
#   returns a list of paths [ images/train , images/test , labels/train , labels/test ]
    image_dir = os.path.join(path, "images")
    image_train_dir = os.path.join(image_dir, train_name)
    image_test_dir = os.path.join(image_dir, test_name)

    label_dir = os.path.join(path, "labels")
    label_train_dir = os.path.join(label_dir, train_name)
    label_test_dir = os.path.join(label_dir, test_name)

    dirs = [image_dir, label_dir, image_train_dir, image_test_dir, \
            label_train_dir, label_test_dir]
    
    for dir in dirs:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)

    return dirs[2:]



def shuffle_dir(paths, permutation):
#   //takes in a list of strings and a list of integers of size n
#   //returns a list of size n where every element at index i is equal to paths[permutation[i]]
#   // e.g. if paths is ["<path>/dir_train","<path>/dir_test"] and permutation is [0,1,0,1,1]
#   // the resulting list would be ["<path>/dir_train","<path>/dir_test","<path>/dir_train","<path>/dir_test","<path>/dir_test"]
# make_permutations(n,[probability_distribution]):
#   // takes in an integer n and a list of floats that sum up to 1
#   // returns a list of size n where each element is an index of probability_distribution, corresponding to a random selection weighted by the said distribution
#   //example, if n is 100, probability_distribution is [0.8,0.2] about 80 percent of the elements in the output should be 0 and 20 percent should be 1
    pass



def save_frames(images, paths, prefix): 
#   // takes in a list of images, and a list of directories to put the frames, which must both be of the same length
#   // and a prefix which should usually be <Datarow_ID>.png
#   // saves the frames, returns the total number of frames if successful, returns -1 if failed.
    if len(images) != len(paths):
        return -1
    for img, path in zip(images, paths):
        res = cv2.imwrite(os.path.join(path, prefix), img)
        if not res:
            return -1
    return len(images)




# write_yolo_annotations([paths], [< Datarow_ID , yolo_label_string >])
#   //takes in a strings "paths" and a list of tuples: Datarow_ID , yolo_label_string
#   //iterates through the list with iterator "i" 
#   //creates a text file in the directory of each "path" with the filename <Datarow_ID>_<i>.txt
#   //and writes yolo_label_string into the contents
# These are functions related to pulling and managing the annotation data:
# pull_datarows(project_id,api_key):
#   //takes in a string project_id, and a string api_key
#   //returns a list of [datarows] where each row, corresponds to a video and its annotation information in the labelbox format
# pull_frames(video_link):
#   //takes in a video link and returns a list of images as numpy arrays
#   //return a list containing [-1] if the video failed to be pulled
# build_class_dict([annotations])
#   //takes in a list of annotations, where each annotation is a dictionary object
#   //returns a dictionary that includes <key:featureId, value:classification> for every featureId in the "annotations" object
# build_yolo_annotations([annotations], {class_dict<featureId,classification>})
#   //takes in a list of annotations and a dictionary, and returns a list of tuples where each tuple is < Datarow_ID , yolo_label_string >
# and of course a run function:
# run (project_id, api_key, path, [dir_names] ...):
#   //Creates the yolo directories
#   //pulls all the datarows
#   //saves all the frames
#   //writes all the annotations