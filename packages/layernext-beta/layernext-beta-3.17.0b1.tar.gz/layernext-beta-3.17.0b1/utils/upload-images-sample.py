import os
import layernext
from dotenv import load_dotenv

from layernext.datalake.constants import MediaType

load_dotenv()  # take environment variables from .env.

api_key = os.environ.get('API_KEY')
secret = os.environ.get('SECRET')
serverUrl = os.environ.get('LAYERX_URL')

client = layernext.LayerNextClient(api_key, secret, serverUrl)

path = "/home/ubuntu/fixelmagic-data/bottle-image-download/test-isuruj-bottle-4/train2017"
# path = "C:/Users/chama/Downloads/training_set/test"
collection_type = MediaType.IMAGE.value
collection_name = "bottle-annotations"
# meta_data_object = {
#     "Captured Location": "test_location",
#     "Camera Id": "aaa",
#     "Tags": [
#         "#retail"
#     ],
#     "bird": "flying"
# }
meta_data_object = {
    "Tags": [
        "bottle"
    ]
}

client.file_upload(path, collection_type, collection_name, meta_data_object)
