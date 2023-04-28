########################IMPORTS STATEMENTS#######################
import numpy as np
import numpy.random 
import shutil, random, os, cv2

######UTILITY FUNCTIONS: FILEWRITING:DIRECTORY STRUCTURE#########

#shuffle_dir([paths],[permutation])
  #takes in a list of strings and a list of integers of size n
  #returns a list of size n where every element at index i is equal to paths[permutation[i]]
  # e.g. if paths is ["<path>/dir_train","<path>/dir_test"] and permutation is [0,1,0,1,1]
  #the resulting list would be ["<path>/dir_train","<path>/dir_test","<path>/dir_train","<path>/dir_test","<path>/dir_test"]
def shuffle_dir(paths, permutation):
    return [paths[p] for p in permutation]

#make_permutations(n,[values],[probability_distribution]):
  #takes in an integer n and a list of floats [values] that sum up to 1
  #returns a list of size n where each element is an index of probability_distribution, corresponding to a random selection weighted by the said distribution
  #example, if n is 100, probability_distribution is [0.8,0.2] about 80 percent of the elements in the output should be 0 and 20 percent should be 1
def make_permutations(n,values, dist):
    return list(np.random.choice(values, size = n, p = dist))

#make_directories(path, train_name, test_name):
  #take in a path, and creates the yolo directory structure
  #returns a list of paths [ images/train , images/test , labels/train , labels/test ]
def make_directories(path, train_name,test_name):
    image_dir = os.path.join(path, "images")
    image_train_dir = os.path.join(image_dir, train_name)
    image_test_dir = os.path.join(image_dir, test_name)

    label_dir = os.path.join(path, "labels")
    label_train_dir = os.path.join(label_dir, train_name)
    label_test_dir = os.path.join(label_dir, test_name)

    dirs = [path, image_dir, label_dir, image_train_dir, image_test_dir, \
            label_train_dir, label_test_dir]
    
    for dir in dirs:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)

    return dirs[3:]

##########UTILITY FUNCTIONS: FILEWRITING: im_list#############

#save_frames([image_list], [paths], prefix): 
  #takes in a list of numpy arrays, and a list of directories to put the frames, which must both be of the same length
  # and a prefix which should usually be <Datarow_ID>.png
  #saves the frames, returns the total number of frames if successful, returns -1 if failed.
def save_frames(im_list, paths, prx): 
  n = len(im_list)
  if n != len(paths):
    return -1
  for img, dir_path, frame in zip(im_list, paths, range(n)):
    full_path = os.path.join(dir_path, prx+'_'+str(frame)+'.png')
    res = cv2.imwrite(full_path, img)
    if not res:
      return -1
  return n

##########UTILITY FUNCTIONS: FILEWRITING: TEXT#############
#write_yolo_annotations([paths], [< Datarow_ID , yolo_label_string >])
  #takes in a strings "paths" and a list of tuples: Datarow_ID , yolo_label_string
  #iterates through the list with iterator "i" 
  #creates a text file in the directory of each "path" with the filename <Datarow_ID>_<i>.txt
  #and writes yolo_label_string into the contents
def write_yolo_annotations(paths, id_label):
  for dir_p, (datarow_id, payload), i in zip(paths, id_label, range(len(id_label))):
    with open(dir_p+os.sep+datarow_id+'_'+str(i)+'.txt', 'w') as file:
      file.write(payload)


