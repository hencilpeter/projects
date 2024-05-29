from openai import OpenAI


class OpenAIClient:
    @staticmethod
    def get_openai_client():
        client = OpenAI(api_key="sk-proj-AkBsYMmRNK4spHW7nwqHT3BlbkFJzU3z6V9QaXyGxtMrXCGP")
        return client
