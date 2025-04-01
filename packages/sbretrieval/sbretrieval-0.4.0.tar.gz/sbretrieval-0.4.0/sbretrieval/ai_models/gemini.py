import os

assert 'GEMINI_API_KEY' in os.environ, 'The environment variable GEMINI_API_KEY is not set'


async def count_tokens(content: str, model: str) -> int:
    '''Counts the tokens of the given content according to the given model.'''

    from google.generativeai import GenerativeModel  # type: ignore[import-untyped]

    client = GenerativeModel(model)
    response = client.count_tokens(content)

    return response.total_tokens


async def generate_embedding(content: str, model: str) -> list[float]:
    '''Generates an embedding of the given content using the given model.'''

    from google.generativeai import embed_content_async

    response = await embed_content_async(model, content)
    response_content = response['embedding']

    return response_content


async def send_prompt(prompt: str, model: str) -> str:
    '''Sends a prompt to the given model and returns its response.'''

    from google.generativeai import GenerativeModel

    client = GenerativeModel(model)
    response = await client.generate_content_async(prompt)
    response_content = response.text

    return response_content
