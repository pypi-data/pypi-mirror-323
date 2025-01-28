import os
import layernext
from dotenv import load_dotenv

from layernext.datalake.constants import MediaType

load_dotenv()  # take environment variables from .env.

api_key = os.environ.get('API_KEY')
secret = os.environ.get('SECRET')
serverUrl = os.environ.get('LAYERX_URL')

# print("serverUrl: ", serverUrl)

client = layernext.LayerNextClient(api_key, secret, serverUrl)

# res = client.download_files_from_metalake("image", "dogs", 0, 1)

# client.upload_metadata_for_files("23-06-SDK-006","/Users/sanduni/Desktop/SDK_Files/metadata_file.json")

# client.upload_metadata_for_unique_name("metadata_file3.json")
client.upload_metadata_by_unique_name("metadata_file3.json")