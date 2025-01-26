from .provider import ProviderFactory


class Client:
    def __init__(self, provider_configs: dict = {}):
        """
        Initialize the client with provider configurations.

        Args:
            provider_configs (dict): Configuration for each provider, e.g.:
                {
                    "openai": {"api_key": "your-openai-api-key"},
                    "huggingface": {"api_key": "your-huggingface-api-key"}
                }
        """
        self.providers = {}
        self.provider_configs = provider_configs
        self._initialize_providers()

    def generate_embeddings(self, model: str, inputs: list, **kwargs):
        """
        Generate embeddings using the specified provider and model.

        Args:
            model (str): Provider and model name in format `provider:model`.
            inputs (list): Text data to embed.

        Returns:
            list: Generated embeddings.
        """
        provider_key, model_name = model.split(":", 1)
        if provider_key not in self.providers:
            config = self.provider_configs.get(provider_key, {})
            self.providers[provider_key] = ProviderFactory.create_provider(
                provider_key, config)
        provider = self.providers[provider_key]
        return provider.generate_embeddings(model_name, inputs, **kwargs)
