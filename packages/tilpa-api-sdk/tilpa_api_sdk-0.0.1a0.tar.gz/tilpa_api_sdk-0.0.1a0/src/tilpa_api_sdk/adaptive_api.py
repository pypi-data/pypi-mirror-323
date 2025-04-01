import os
import shutil
import time
import signal
from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import requests
import uvicorn
import threading
import firebase_admin
import openai
from firebase_admin import credentials, firestore


API_URL = "https://tilpa-api-server.onrender.com"

class GenerationResponse(BaseModel):
    """
    Represents a response to a code generation request.

    Attributes:
        code (str): The generated code block as a string.
        endpoint_name (str): The name of the generated endpoint.
        imports_needed (List[str]): A list of imports required for the generated code block.
        libraries (List[str]): A list of libraries required for the generated code block.
        methods (List[str]): A list of methods required for the generated code block.
    """

    code: str
    endpoint_name: str
    libraries: List[str]
    methods: List[str]


class GenerationRequest(BaseModel):
    """
    Represents a request to generate an endpoint.

    Attributes:
        prompt (str): The feature description to generate an endpoint for.
        max_tokens (Optional[int], optional): The maximum number of tokens to generate. Defaults to 1000.
        temperature (Optional[float], optional): The temperature to control the randomness of the generation. Defaults to 0.2.
    """

    prompt: str
    open_ai_client: Optional[bool] = False
    firestore_db: Optional[bool] = False
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0


class Adaptive_API:
    """
    The main class for the Adaptive API
    """

    def __init__(
        self,
        adaptive_api_key: str,
        open_ai_key: Optional[str] = None,
        port: Optional[int] = 8000,
        path_to_service_account_key: Optional[str] = None,
    ):
        self.path_to_service_account_key = path_to_service_account_key
        self.adaptive_api_key = adaptive_api_key
        self.open_ai_key = open_ai_key
        self.port = port
        self.server_thread = None
        self.db = None
        self.client = None
        self.server = None

        if self.adaptive_api_key is None:
            raise ValueError("adaptive_api_key is required")

        self.app = FastAPI()

        if self.path_to_service_account_key is not None:
            self.cred = credentials.Certificate(self.path_to_service_account_key)
            firebase_admin.initialize_app(self.cred)
            self.db = firestore.client()
            print("Firebase initialized")

        if self.open_ai_key is not None:
            self.client = openai.Client(api_key=self.open_ai_key)
            print("OpenAI client initialized")

        # To keep track of features, use a set
        self.routes = set()

    def generate(
        self,
        request: GenerationRequest,
    ):
        response = requests.post(
            url=API_URL + "/generate",
            json={
                "prompt": request.prompt,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "open_ai_client": request.open_ai_client,
                "firestore_db": request.firestore_db,
            },
            headers={
                "Authorization": f"Bearer {self.adaptive_api_key}",
                "Content-type": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()
        return GenerationResponse(**response.json())

    def start(self):
        @self.app.post("/generate")
        async def generate(request: GenerationRequest):
            response = self.generate(
                request
            )
            return response
        
        @self.app.post("/shutdown")
        async def shutdown():
            self.shutdown()
            return {"message": "Shutting down"}

        def run_server():
            config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port)
            self.server = uvicorn.Server(config)
            self.server.run()

        def handle_sigint(signum, frame):
            self.shutdown()

        signal.signal(signal.SIGINT, handle_sigint)

        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.start()
        time.sleep(1)

    def shutdown(self):
        # delete all features
        for file in os.listdir("features"):
            file_path = os.path.join("features", file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        if self.server:
            self.server.should_exit = True
            self.server.force_exit = True
            self.server_thread.join(timeout=1)
            print("\n\n\n\n\n")
            print("Shutting down...")
            print("\n\n\n\n\n")
            raise SystemExit

    def execute_external_code(self, file_path):
        try:
            with open(file_path, 'r') as file:
                code = file.read()
            # Create a local execution context and pass `self`
            local_context = {'self': self}
            exec(code, {'self': self}, {})
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def add_feature(self, prompt):
        open_ai_client = True if self.client is not None else False
        firestore_db = True if self.db is not None else False
        response = self.generate(GenerationRequest(prompt=prompt, open_ai_client=open_ai_client, firestore_db=firestore_db))
        print("Code block:\n")
        print(response.code)
        print("\n\n")

        print("Endpoint name:")
        print(response.endpoint_name)
        print("\n\n")

        print("Libraries needed:")
        print(response.libraries)
        print("\n\n")

        # add feature to routes
        self.routes.add(response.endpoint_name)

        # install dependencies
        os.system(f"pip install {' '.join(response.libraries)}")

        # make features directory
        if not os.path.exists("features"):
            os.makedirs("features")

        # write code to file
        if not os.path.exists(f"features/{response.endpoint_name}.py"):
            with open(f"features/{response.endpoint_name}.py", "w") as f:
                f.write(response.code)

        # execute code
        self.execute_external_code(f"features/{response.endpoint_name}.py")

        return response.endpoint_name, response.methods
