import os
import layernext
# from dotenv import load_dotenv
import numpy as np

from layernext.datalake.constants import MediaType

# load_dotenv()  # take environment variables from .env.

API_KEY="key_kh6mm38zb2sfxgc4ntpsgkp356o0dfso"
SECRET="oal2ylui88d0w0rf1zrj"
# LAYERX_URL="https://api.dev.layernext.ai"
LAYERX_URL="http://localhost"

client = layernext.LayerNextClient(API_KEY, SECRET, LAYERX_URL)

for i in range(0, 200*1000, 1000):
    data = []
    for j in range(1000):
        data.append({
            "uniqueName": f'{i+j}',
            "embeddings": np.random.rand(2048).astype(np.float32)
        })


