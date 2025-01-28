import os
# from dotenv import load_dotenv
# import numpy as np
from datetime import datetime, timedelta

from layernext import LayerNextClient
# load_dotenv()  # take environment variables from .env.

API_KEY="key_yyq1jzhjv7o4ixqrj4hleh27k6s9o4qv"
SECRET="rzx8knm2q6j8dxrhtuk7"
LAYERX_URL="https://api.dev-llm.layernext.ai"
# LAYERX_URL="http://127.0.0.1:3000"
# URL="http://127.0.0.1:3000"





client = LayerNextClient(API_KEY, SECRET, LAYERX_URL)
# client = LayerNextClient(API_KEY, SECRET_KEY, URL)






# ------------------------------------------------------------------------------------------------------------------------------------------------
# Prepare the date range for the test
# yesterday = datetime.now() - timedelta(days=1)
# start_of_yesterday = yesterday.replace(hour=6, minute=0, second=0)
# end_of_yesterday = start_of_yesterday + timedelta(days=1)

# Define the aggregation pipeline to match the one in the pdrmax_job_forecast.py script
# jobs_completed_pipeline = [
#     {"$match": {"completedAt": {"$gte": start_of_yesterday, "$lt": end_of_yesterday}}},
#     {"$count": "completed_jobs"},
# ]

# Define the collection name to match the one in the script
# collection_name = "Job"

# Execute the aggregation using the SDK's run_mongodb_aggregation function
# res = client.run_mongodb_aggregation("DCCHail", jobs_completed_pipeline, collection_name)

# Print the result of the aggregation
# print(f"Completed Jobs Aggregation Result: {res}")
# -----------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------------------

# unique_list = [
#     "chat_Mahela Panduka Bandara_2ab6b694-7e2a-4f98-8e05-5e3638ed727b.pdf"
# ]
#res = client.find_elements(unique_list, "What is the university of Mahela?")
# res = client.retrieve_documents_with_structure(["resume"], ["Mahela Panduka Bandara"], "What is the university of Mahela?" )
# -----------------------------------------------------------------------------------------------------------------------
# data=[
#     { "date": "2024-08-01", "count": 15 },
#     { "date": "2024-08-02", "count": 20 },
#     { "date": "2024-08-03", "count": 25 }
# ]
# res = client.insert_mongodb_data("sales-data","LN_ForecastedDailyRevenue",data)
# res =client.delete_mongodb_data("sales-data","LN_ForecastedDailyRevenue",{})
# print(res)

# -----------------------------------------------------------------------------------------------------------------------------------
# Define a sample pipeline for aggregation
# This pipeline will simply count the number of documents in the collection
# pipeline = [
#     {"$match": {}},  # Match all documents
#     {"$count": "total_documents"}  # Count the total number of documents
# ]

# ------------------------------------------------------------------------------------------------------------------------------------
# Test the aggregation on the LN_ForecastedDailyCompletedJobs collection
# collection_name = "LN_ForecastedDailyCompletedJobs"
# res_completed_jobs = client.run_mongodb_aggregation("sales-data", pipeline, collection_name)
# print(f"Completed Jobs Aggregation Result: {res_completed_jobs}")
# ------------------------------------------------------------------------------------------------------------------------------------
# Test the aggregation on the LN_ForecastedDailyRevenue collection
# collection_name = "LN_ForecastedDailyRevenue"
# res_revenue = client.run_mongodb_aggregation("sales-data", pipeline, collection_name)
# print(f"Revenue Aggregation Result: {res_revenue}")
# ------------------------------------------------------------------------------------------------------------------------------------