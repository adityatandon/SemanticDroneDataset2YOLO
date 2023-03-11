# Code to read annotations of persons from the Semantic Drone dataset in LabelMe XML
# format and convert these annotations to labels in the YOLO format
#
# Download the original TU Graz - Semantic Drone dataset with annotations for persons
# The dataset can be downloaded at https://dronedataset.icg.tugraz.at/ 
#
# Add the images and corresponding annotations to the folders before using this script
#
# Follow this directory structure to use this code as-is
# 
# └── working directory 
#      └── SemanticDroneDataset2YOLO.py
#      └── viewConvertedLabels.py
#      └── semantic_drone_dataset
#               └── training_set
#                   └── gt
#                   |   └── bounding_box
#                   |       └── label_me_xml (contains the original annotations)
#                   |       └── labels (will be created)
#                   └── images

import xml.etree.ElementTree as ET
import glob
import os


def convert_annotation(x_min, x_max, y_min, y_max, image_width, image_height):

    x_center = ((x_max + x_min) / 2) / image_width
    y_center = ((y_max + y_min) / 2) / image_height
    width = (x_max - x_min) / image_width
    height = (y_max - y_min) / image_height

    return [x_center, y_center, width, height]


input_dir = "semantic_drone_dataset/training_data/gt/bounding_box/label_me_xml/"
output_dir = "semantic_drone_dataset/training_data/gt/bounding_box/labels/"
image_dir = "semantic_drone_dataset/training_data/images/"
classes = []

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

files = glob.glob(os.path.join(input_dir, '*.xml'))

for file in files:
    basename = os.path.basename(file)
    filename = os.path.splitext(basename)[0]
    print(filename)

    yolo_annotation_string = []

    tree = ET.parse(file)
    root = tree.getroot()

    image_width = int(root.find("imagesize").find("ncols").text)
    image_height = int(root.find("imagesize").find("nrows").text)

    for object in root.findall('object'):
        label = object.find("name").text

        # check for new classes and append to class list
        if label not in classes:
            classes.append(label)
        index = classes.index(label)

        x_points = []
        y_points = []

        for polygon in object.findall("polygon"):
            for point in polygon.findall("pt"):
                for x_coord in point.findall("x"):
                    x_points.append(round(int(x_coord.text)))
                for y_coord in point.findall("y"):
                    y_points.append(round(int(y_coord.text)))

            x_max = max(x_points)
            x_min = min(x_points)
            y_max = max(y_points)
            y_min = min(y_points)

            yolo_bounding_box = convert_annotation(x_min, x_max, y_min, y_max, image_width, image_height)
            bounding_box_string = " ".join([str(x) for x in yolo_bounding_box])
            yolo_annotation_string.append(f"{index} {bounding_box_string}")
    
    
    # Generate a text file in YOLO format for each LabelMe XML file
    # If annotations do not exist in the XML file, an empty text file is created
    with open(os.path.join(output_dir, f"{filename}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(yolo_annotation_string))

