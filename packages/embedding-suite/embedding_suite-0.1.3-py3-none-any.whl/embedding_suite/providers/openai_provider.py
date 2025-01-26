import openai
from embedding_suite.provider import Provider
from embedding_suite.utils.config import get_api_key


class OpenaiProvider(Provider):
    def __init__(self, **config):
        # Get the API key from the environment or config
        self.api_key = config.get("api_key") or get_api_key("openai")
        if not self.api_key:
            raise ValueError("OpenAI API key is missing.")

        # Set OpenAI's API key
        openai.api_key = self.api_key

    def generate_embeddings(self, model, inputs, **kwargs):
        response = openai.Embedding.create(model=model, input=inputs, **kwargs)
        return [item["embedding"] for item in response["data"]]
