"""
dataformat_utils.py

Functions for creating conversion tools

"""
import os
import sys
import json
import PIL
import numpy as np
from shutil import copyfile
from pyquaternion import Quaternion
from scipy.spatial.transform import Rotation as R
import math

ORIGIN = 0
SIZE = 1
ROTATION = 2
ANNOTATION = 3
CONFIDENCE = 4
COLOR = 5

def create_lct_directory(path, name):
    """Create top level LCT directory at specified path
    Args:
        path: target path where directory will be stored
        name: the name of the new directory to create
    Returns:
        None
        """
    sub_directories = ['cameras', 'pointcloud', 'bounding', 'pred_bounding', 'ego']
    try:
        parent_path = os.path.join(path, name)
        os.makedirs(parent_path, exist_ok=True)

        # Create each sub directory
        for directory in sub_directories:
            full_path = os.path.join(parent_path, directory)
            os.makedirs(full_path, exist_ok=True)

    except OSError as error:
        print(error)
        sys.exit(1)

def create_rgb_sensor_directory(path, name, translation, rotation, intrinsic):
    """Adds one RGB sensor directory inside camera directory, and adds extrinsic/intrinsic data for said sensor
    Args:
        path: path to LCT directory
        name: name of RGB sensor
        translation: [x,y,z] list representing sensor translation
        rotation: [w,x,y,z] quaternion representing sensor rotation
        intrinsic: [3,3] 3x3 2D List representing intrinsic matrix
    Returns:
        None
        """

    # Create necessary directory: ./Cameras/[name]
    work_dir = os.path.join(path, "cameras", name)

    os.makedirs(work_dir, exist_ok=True)

    # Creates the Extrinsic.json file in the /Cameras/[name] directory from the
    # translation and rotation parameters.
    extrinsics = {}
    extrinsics['translation'] = translation
    extrinsics['rotation'] = rotation

    with open(work_dir + "/extrinsics.json", "w") as extrinsic_file:
        extrinsic_file.write(json.dumps(extrinsics))

    # Creates the Extrinsic.json file in the /Cameras/[name] directory from the intrinsic parameter.
    with open(work_dir + "/intrinsics.json", "w") as intrinsic_file:
        intrinsic_file.write(json.dumps({"matrix" : intrinsic}))


def add_rgb_frame(path, name, frame_num, image):
    """Adds one jpg from one frame to the structure inside the camera directory for a given sensor
    Args:
        path: path to LCT directory
        name: name of RGB sensor
        frame_num: the number corresponding to the frame
        images: a PIL image object containing image data
    Returns:
        None
        """

    image.save(os.path.join(os.path.join(os.path.join(path, "cameras"), name),
    str(frame_num) +".jpg"))

def add_rgb_frame_from_jpg(path, name, frame_num, input_path):
    """Copies existing jpg file into the cameras directory
    Args:
        path: path to LCT directory
        name: name of RGB sensor
        frame_num: the number corresponding to the frame
        input_path: Path to source jpg iamge
    Returns:
        None
        """
    
    full_path = os.path.join(path, 'cameras', name, str(frame_num) + '.jpg')
    copyfile(input_path, full_path)

def create_lidar_sensor_directory(path, name):
    """Creates directory for one LiDAR sensor
    Args:
        path: path to LCT directory
        name: name of LiDAR sensor
    Returns:
        None
        """

    full_path = os.path.join(path, 'pointcloud', name)
    os.makedirs(full_path, exist_ok=True)

def add_lidar_frame(path, name, frame_num, points, translation, rotation):
    """Adds one lidar sensor directory inside pointcloud directory
    Args:
        path: path to LCT directory
        name: name of LiDAR sensor
        frame_num: frame number
        points: [n, 3] list of (x,y,z) tuples representing x,y,z coordinates
        translation: [x,y,z] list representing sensor translation
        rotation: [w,x,y,z] quaternion representing sensor rotation
    Returns:
        None
        """

    # Build a .pcd file line by line
    # See .pcd file format documentation at https://pointclouds.org/documentation/tutorials/pcd_file_format.html
    pcd_lines = ['# .PCD v0.7 - Point Cloud Data file format', 'VERSION 0.7', 'FIELDS x y z',
                'SIZE 4 4 4', 'TYPE F F F', 'COUNT 1 1 1']
    pcd_lines.append('WIDTH ' + str(len(points)))
    pcd_lines.append('HEIGHT 1')
    pcd_lines.append('VIEWPOINT ' + ' '.join([str(i) for i in translation + rotation]))
    pcd_lines.append('POINTS ' + str(len(points)))
    pcd_lines.append('DATA ascii')
    for point in points:
        pcd_lines.append(' '.join([str(i) for i in point]))
    
    pcd_str = '\n'.join(pcd_lines)

    full_path = os.path.join(path, 'pointcloud', name, str(frame_num) + '.pcd')
    
    with open(full_path, 'w') as f:
        f.write(pcd_str)

def add_lidar_frame_from_pcd(path, name, frame_num, input_path):
    """Copies one .pcd file to pointcloud directory
    Args:
        path: path to LCT directory
        name: name of LiDAR sensor
        frame_num: frame number
        input_path: path to PCD file
    Returns:
        None
        """
    
    full_path = os.path.join(path, 'pointcloud', name, str(frame_num) + '.pcd')
    copyfile(input_path, full_path)

def create_frame_bounding_directory(path, frame_num, origins, sizes, rotations, annotation_names, confidences, predicted=False):   
    """Adds box data for one frame
    Args:
        path: path to LCT directory
        frame_num: frame index (0-indexed) (will overwrite if duplicate frames are specified)
        origins: [n, 3] list representing x,y,z coordinates of the center of the boxes
        sizes: [n, 3] list representing W,L,H of box
        rotations:[n, 4] list of quaternions representing box rotation with respect to (0,0,0)
        annotation_names: list of length n where every element is a string with the name of the bounding box
        confidence: list of length n of integers where every element is a value from 0-100 representing the confidence percentage
            should be 101 for ground truth.
        origins, sizes, rotations, annotation_names, confidences should all be the same size
        predicted: Optional argument that specifies that this data is predicted data
    Returns:
        None
        """

    # Check that all lists are the same size
    lengths = [len(origins), len(sizes), len(rotations), len(annotation_names), len(confidences)]
    if lengths.count(len(origins)) != len(lengths):
        print("Frame_Bounding_Directory(): Length of lists is not equal!")
        sys.exit(2)

    # Create directory that stores the boxes in one frame
    if predicted:
        full_path = os.path.join(path, 'pred_bounding', str(frame_num))
    else:
        full_path = os.path.join(path, 'bounding', str(frame_num))
    os.makedirs(full_path, exist_ok=True)
    
    # Create description.json
    description = {}
    description['num_boxes'] = len(origins)
    description_path = os.path.join(full_path, 'description.json')
    with open(description_path, 'w') as f:
        json.dump(description, f)

    # Creates JSON file that stores all the boxes in a frame 

    json_name = 'boxes.json'
    json_path = os.path.join(full_path, json_name)
    box_data = {}
    box_data['boxes'] = []
    for i in range(0, len(origins)):
        box = {}
        box['origin'] = origins[i]
        box['size'] = sizes[i]
        box['rotation'] = rotations[i]
        box['annotation'] = annotation_names[i]
        box['confidence'] = confidences[i]
        box_data['boxes'].append(box)

    with open(json_path, 'w') as f:
        json.dump(box_data, f)

def create_annotation_map(path, annotation_map):
    """Specifies the correct relationship between GT annotation names and Predicted names.
    Args:
        path: path to LCT dir
        annotation_map: dictionary that represents correct annotation mapping where the key is a GT annotation name that points
            to a list of corresponding predicted names. ex: annotation_map['vehicle.car'] = [car].
    """
    json_name = 'annotation_map.json'
    json_path = os.path.join(path, 'pred_bounding', json_name)
    with open(json_path, 'w') as f:
        json.dump(annotation_map, f)

        
def create_ego_directory(path, frame, translation, rotation):
    """Adds ego data for one frame
    Args:
        path: path to LCT dir
        frame: Frame number for ego data
        translation: [x,y,z] that represents translation
        rotation: [w,x,y,z] that represents rotation
    Returns:
        None
        """
    # Join path to ego dir
    full_path = os.path.join(path, 'ego')

    # Add json file for frame number
    json_path = os.path.join(full_path, str(frame) + '.json')
    ego_data = {}
    ego_data['translation'] = translation
    ego_data['rotation'] = rotation

    with open(json_path, 'w') as f:
        json.dump(ego_data, f)




def print_progress_bar(frame_num, total):
    """Prints a progress bar
    Args:
        frame_num: current frame number
        total: number of frames
    Returns:
        None
        """

    length = 40

    # Adjust size of progress bar based on console size
    if os.get_terminal_size()[0] < 50:
        length = 10
    elif os.get_terminal_size()[0] < 70:
        length = 20
    
    filled_length = (length * frame_num//total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\rConverting: {bar} {frame_num}/{total} frames', end = '\r')
    
    # After progress is complete run a new line
    if frame_num == total: 
        print()