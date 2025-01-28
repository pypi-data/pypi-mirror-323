import layernext
api_key = 'key_nuzplkko0b5jvdzp38c9uwfce5glr0lk'
secret = '7yu90ssqspkou9y6mpe1'
url = 'https://api.macdon.layernext.ai'
import json
import layernext
import wget
import time

def label_rename(src_text):
    rename_dict = {
        "2db977d6-599c-4886-a4c5-8c7b86bc4a8b":"Upper Cross Auger",
        "468ff4bb-29e5-4c81-95ba-89e94e42fc3a": "Backtube",
        "bd851499-7ab2-4e22-b6f2-bf9de2b3ba65": "Draper",
        "9fc028cd-5f35-4233-9f8e-5f97bde734bb": "Reel",
        "1f1c2fb3-39ae-43ab-8839-608796b480db": "Crop"
    }
    if src_text in rename_dict:
        return rename_dict[src_text]
    else:
        return src_text


project_id ="62f126ae8e1272bbf43423b4"
project_name = "Header Segmentation 3-reel wheat"

meta_data_object = {
    "LayerNext Annotation Project ID": project_id
}

client = layernext.LayerNextClient(api_key, secret, url)
client.file_upload('/home/ubuntu/layernext/python-test/macdon_projects/' + project_id,5, project_name, meta_data_object, True)
print('File upload done')
#time.sleep(30)


f = open('sample-' + project_id + '.json')

data = json.load(f)
images_with_annotations = []

annotation_task_list = data["data"]
for task in annotation_task_list:
    task_id = task["task_id"]
    frame_list = task["frames"]
    for frame in frame_list:
        file_name = task_id + "_" + str(frame["frameId"]) + ".jpeg"
        image_with_anno = {
            'image': file_name,
            'annotations': []
        }

        for _annotation in frame['shapes']:
            formatted_annotation = {
                'polygon': _annotation['points'],
                'label': label_rename(_annotation['label']),
                'metadata': {}
            }

            image_with_anno['annotations'].append(formatted_annotation)
        images_with_annotations.append(image_with_anno)

output = {
    "images": images_with_annotations
}

with open("annotations_" + project_id + ".json", 'w') as file:
    file.write(json.dumps(output))


    client.upload_annoations_for_folder(project_name,project_id, 'annotations_'+project_id + '.json', 'polygon', False, False)
