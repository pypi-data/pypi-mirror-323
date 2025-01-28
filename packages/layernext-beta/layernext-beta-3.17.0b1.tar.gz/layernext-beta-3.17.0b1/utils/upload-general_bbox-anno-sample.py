import os
import layernext
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

formatted_anno_json_path = os.environ.get('ANNO_FILE_TO_UPLOAD')

# upload annotations
api_key = os.environ.get('API_KEY')
secret = os.environ.get('SECRET')
serverUrl = os.environ.get('LAYERX_URL')

client = layernext.LayerNextClient(api_key, secret, serverUrl)

print("Uploading annotations to layernext")

client.upload_annoations_for_folder("sample-pack_images", "sample-pack_event", formatted_anno_json_path, "rectangle", False, False)


