import json
import layernext
import wget
import requests
project_id="62224601701c33c62cd575d2"
f = open('sample-' + project_id +'.json')

data = json.load(f)

annotation_task_list = data["data"]
for task in annotation_task_list:
    task_id = task["task_id"]
    frame_list = task["frames"]
    for frame in frame_list:
        print(f"Image url = {frame['imageAnnotationUrl']}")
        image_url = frame['imageAnnotationUrl']
        save_path = "macdon_projects/" + project_id + "/" + task_id + "_" + str(frame["frameId"]) + ".jpeg"
        img_data = requests.get(image_url).content
        with open(save_path, 'wb') as handler:
            handler.write(img_data)

