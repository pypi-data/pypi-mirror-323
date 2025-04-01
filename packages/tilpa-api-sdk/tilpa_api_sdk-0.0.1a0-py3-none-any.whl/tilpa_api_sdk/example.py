from adaptive_api import Adaptive_API

# Example of how to initialize the Adaptive_API class
adaptive_api = Adaptive_API(
    adaptive_api_key="your_adaptive_api_key",
    open_ai_key="your_openai_api_key"
)

adaptive_api.start()
adaptive_api.add_feature("Make an endpoint that gives nutritional advice based on the http request")