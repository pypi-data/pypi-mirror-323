import json
import os
import random
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

file_path = os.environ.get('PREDICTION_FILE_TO_FORMAT')

# load json file
f = open(file_path)
data = json.load(f)
f.close()


output = {
    "images": []
}

images_dict = data['images']
for img in images_dict.values():
    print(img)
    anno_dict = img['annotations']
    _anno = []
    for anno in anno_dict.values():
        print(anno)
        _anno.append(anno)

    output['images'].append(
        {
            'image': img['image'],
            'annotations': _anno
        }
    )

with open(os.environ.get('PREDICTION_FILE_TO_UPLOAD'), 'w') as file:
    file.write(json.dumps(output))
