import os
import layernext
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

# api_key = os.environ.get('API_KEY')
# secret = os.environ.get('SECRET')
# serverUrl = os.environ.get('DATALAKE_URL')
api_key = "key_plgni1hwply7gjyvng9ixenfjw8dybzl"
secret = "6k74dfbd48391axc8xp5"
serverUrl = 'https://api.dev.layernext.ai'

client = layernext.LayerNextClient(api_key, secret, serverUrl)

"""
@param collection_id - dataset version id
"""
client.download_annotations("63919028e1cb210775cafe6e", 'dec-6-0.0.1')