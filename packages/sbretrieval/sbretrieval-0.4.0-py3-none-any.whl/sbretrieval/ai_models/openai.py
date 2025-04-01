from typing import cast
import os

assert 'OPENAI_API_KEY' in os.environ, 'The environment variable OPENAI_API_KEY is not set'


async def count_tokens(content: str, model: str) -> int:
    '''Counts the tokens of the given content according to the given model.'''

    from tiktoken import encoding_for_model

    encoding = encoding_for_model(model)
    tokens = encoding.encode(content)

    return len(tokens)


async def generate_embedding(content: str, model: str) -> list[float]:
    '''Generates an embedding of the given content using the given model.'''

    from openai import AsyncOpenAI

    client = AsyncOpenAI()
    response = await client.embeddings.create(model=model, input=content, encoding_format='float')
    response_content = response.data[0].embedding

    return response_content


async def send_prompt(prompt: str, model: str) -> str:
    '''Sends a prompt to the given model and returns its response.'''

    from openai import AsyncOpenAI

    messages = [{'role': 'user', 'content': prompt}]

    client = AsyncOpenAI()
    response = await client.chat.completions.create(model=model, messages=messages)  # type: ignore[arg-type]
    response_content = response.choices[0].message.content

    return cast(str, response_content)
