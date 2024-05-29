from openai import OpenAI


class OpenAIClient:
    @staticmethod
    def get_openai_client():
        client = OpenAI(api_key="sk")
        return client
