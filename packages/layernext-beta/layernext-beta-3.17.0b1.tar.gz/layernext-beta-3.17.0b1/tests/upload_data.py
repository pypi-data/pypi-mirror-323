import os
import layernext
#from dotenv import load_dotenv

from layernext.datalake.constants import MediaType

# load_dotenv()  # take environment variables from .env.

API_KEY="key_kh6mm38zb2sfxgc4ntpsgkp356o0dfso"
SECRET="oal2ylui88d0w0rf1zrj"
LAYERX_URL="https://api.dev.layernext.ai"

client = layernext.LayerNextClient(API_KEY, SECRET, LAYERX_URL)

# file_path = "/Users/chathushka/Desktop/Projects-zoomi/media/files"
# json_data_file_path = "/Users/chathushka/Desktop/Projects-zoomi/media/annotation.json"

# collection_type = MediaType.IMAGE.value
# collection_name = "dec-23-001"
# meta_data_object = {
#     "Captured Location": "test_location",
#     "Camera Id": "007",
#     "Tags": [
#         "#retail"
#     ],
#     "test": "test"
# }

# client.upload_data(collection_name, file_path, meta_data_object, 'dec-6-0.0.1',json_data_file_path, 'rectangle', False, True)
# client.upload_annoations_for_folder(collection_name, 'dec-6-0.0.1', json_data_file_path, 'rectangle', False, True)
# status = client.get_upload_status(collection_name)
# print(status)

# client.register_model("/Users/chathushka/Desktop/Projects-zoomi/layerx-python-sdk/tests/model_test", "model_007")
# details = client.get_collection_details("64f59d0bbc8118beeb50d2f7", {"frameCount": True, "fileSize": True})
# print(details)
# client.auto_tag_collection("63be44db0d00869375f18135","model_006")#64f59d0bbc8118beeb50d2f7
#63be44db0d00869375f18135s