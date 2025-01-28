import json
import os
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

file_path = os.environ.get('ANNO_FILE_TO_FORMAT')
# load json file
f = open(file_path)
data = json.load(f)
f.close()

anno_meta = data['metaData']
anno_data = data['data']

images_with_annotations = []

i = 0
for task in anno_data:
    task_id = task['task_id']
    task_anno_data = task['frames']
    for frame in task_anno_data:
        image_with_anno = {
            'image': f'{task_id}_{frame["frameId"]}.jpg',
            'annotations': []
        }
        # print(frame)
        for _annotation in frame['shapes']:
            # print(_annotation)
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
    i+=1
    print(f"Printing task {i} - {task_id} complete \n----------------------------------------------------------")

output = {
    "images": images_with_annotations
}

formatted_anno_json_path = os.environ.get('ANNO_FILE_TO_UPLOAD')
# save as formatted json
with open(formatted_anno_json_path, 'w') as file:
    file.write(json.dumps(output))
print(f"Saved formatted annotations file: {formatted_anno_json_path}")

