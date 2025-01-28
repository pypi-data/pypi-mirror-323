import os
import layernext
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

api_key = os.environ.get('API_KEY')
secret = os.environ.get('SECRET')
serverUrl = os.environ.get('LAYERX_URL')

client = layernext.LayerNextClient(api_key, secret, serverUrl)

"""
@param version_id - dataset version id
@param export_type - dataset export format
"""
# client.download_dataset("656701b378ec49821bff632a", "YOLO Darknet", "YOLO")
# client.download_dataset("6566c5304a2b92d4278099c0", "RAW", "RAW")
# client.download_dataset("6566cab7c7f118e46f11938e", "Semantic Segmentation", "SEM")
# key = client.get_downloadable_url("11_29-Dataset-down-003_656701b378ec49010bff6329_656701b378ec49821bff632a_YOLO_Darknet_11-29-Test-01_pexels-pixabay-33287.txt")
# print(key)

# embedding_list = [{
#   "uniqueName": "lahiru test_dogs.jpg",
#   "embeddings": [0.23]
# }]

# res = client.insert_image_embeddings(embedding_list, "dimOne", [1])

# res = client.get_item_count_from_collection("6569b51bdfe0e538a42519db")
# res = client.generate_embeddings_for_collection("6555baadb5a29671f1aa50e6", "Resnet50")

res=client.create_annotation_project_from_collection("12-04-Test-car-fps-01", "656d59b6aadb70e3050a47e6", "metadata.Tags=v-01", {}, 20)

print(res)