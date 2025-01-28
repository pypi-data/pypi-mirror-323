import json
import os
import random
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

file_path = os.environ.get('FILE_TO_FORMAT')

# load json file
f = open(file_path)
data = json.load(f)
f.close()

categories = data['categories']
categories_to_id_dict = {}
for _cat in categories:
    categories_to_id_dict[_cat['id']] = _cat

annotations = data['annotations']
annotations_to_image_id_dict = {}
for _anno in annotations:
    if _anno['image_id'] not in annotations_to_image_id_dict:
        annotations_to_image_id_dict[_anno['image_id']] = []
    annotations_to_image_id_dict[_anno['image_id']].append(_anno)

images = data['images']
images_with_annotations = []

for image in images:
    if image['id'] in annotations_to_image_id_dict:
        image_with_anno = {
            'image': image['file_name'],
            'annotations': []
        }
        for _annotation in annotations_to_image_id_dict[image['id']]:
            if 'segmentation' in _annotation \
                    and type(_annotation['segmentation']) is list \
                    and len(_annotation['segmentation']) > 0:
                _segmentation = _annotation['segmentation']
                polygon_points = []
                xy = []
                for x_or_y in _segmentation[0]:
                    xy.append(x_or_y)
                    if len(xy) == 2:
                        polygon_points.append(xy)
                        xy = []

                formatted_annotation = {
                    'polygon': polygon_points,
                    'label': categories_to_id_dict[_annotation['category_id']]['supercategory'],
                    'metadata': {
                        'name': categories_to_id_dict[_annotation['category_id']]['name']
                    },
                    'confidence': random.random()
                }
                image_with_anno['annotations'].append(formatted_annotation)
        images_with_annotations.append(image_with_anno)

output = {
    "images": images_with_annotations
}

with open(os.environ.get('FILE_TO_UPLOAD'), 'w') as file:
    file.write(json.dumps(output))
