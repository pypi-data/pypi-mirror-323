from adaptive_api import Adaptive_API
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
adaptive_api_key = os.getenv("ADAPTIVE_API_KEY")

adaptive_api = Adaptive_API(
    adaptive_api_key=adaptive_api_key,
    path_to_service_account_key="../../serviceAccountKey.json",
    open_ai_key=os.getenv("OPENAI_API_KEY"),
)

# test api start and feature generation
adaptive_api.start()
adaptive_api.add_feature("make an api endpoint that takes a string and returns the string reversed")

# test openai client
adaptive_api.add_feature("make an api endpoint that summarizes a prompt")

# test firestore db
adaptive_api.add_feature("make an api endpoint that stores a string in a firestore database")

# test api stop
# adaptive_api.shutdown()