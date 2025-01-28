import os
import layernext
from dotenv import load_dotenv

from layernext.datalake.constants import MediaType

load_dotenv()  # take environment variables from .env.

# api_key = os.environ.get('API_KEY')
# secret = os.environ.get('SECRET')
# serverUrl = os.environ.get('LAYERX_URL')
api_key = "key_plgni1hwply7gjyvng9ixenfjw8dybzl"
secret = "6k74dfbd48391axc8xp5"
# serverUrl = 'https://api.dev.layernext.ai'
serverUrl = 'http://[::1]:3000'

client = layernext.LayerNextClient(api_key, secret, serverUrl)

file_path = "/Users/chathushka/Desktop/Projects-zoomi/media/files"
json_data_file_path = "/Users/chathushka/Desktop/Projects-zoomi/media/annotation.json"

collection_type = MediaType.IMAGE.value
collection_name = "dec-08-002"
meta_data_object = {
    "Captured Location": "test_location",
    "Camera Id": "007",
    "Tags": [
        "#retail"
    ],
    "test": "test"
}

# client.upload_data(collection_name, file_path, meta_data_object, 'dec-6-0.0.1',json_data_file_path, 'rectangle', False, False)
# status = client.get_upload_status(collection_name)
# print(status)
client.remove_annotations("6392d255df7d376a9b6cc492", "dec-6-0.0.1")