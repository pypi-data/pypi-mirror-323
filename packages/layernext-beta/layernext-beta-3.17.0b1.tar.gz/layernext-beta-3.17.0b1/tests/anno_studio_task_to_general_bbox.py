import json
import os
import random
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

file_path = os.environ.get('ANNO_FILE_TO_FORMAT')

# load json file
f = open(file_path)
data = json.load(f)
f.close()

anno_meta = data['metaData']
anno_data = data['data']

task_id = anno_meta['task_id']

images_with_annotations = []

for frame in anno_data:
    image_with_anno = {
        'image': f'{task_id}_{frame["frameId"]}.jpg',
        'annotations': []
    }
    print(frame)
    for _annotation in frame['shapes']:
        print(_annotation)
        formatted_annotation = {
            'bbox': [
                _annotation['boundaries']['x'],
                _annotation['boundaries']['y'],
                _annotation['boundaries']['w'],
                _annotation['boundaries']['h'],
            ],
            'label': _annotation['label'],
            'metadata': _annotation['attributeValues']
        }
        image_with_anno['annotations'].append(formatted_annotation)
    images_with_annotations.append(image_with_anno)

output = {
    "images": images_with_annotations
}

with open(os.environ.get('ANNO_FILE_TO_UPLOAD'), 'w') as file:
    file.write(json.dumps(output))
