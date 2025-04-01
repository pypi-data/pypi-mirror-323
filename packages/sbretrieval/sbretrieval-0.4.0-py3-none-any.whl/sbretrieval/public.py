from typing import Optional

from asyncpg import Connection  # type: ignore[import-untyped]

from sbretrieval.ai_models import load_module_by_vendor
from sbretrieval.database import delete_document, search_documents_by_embeddings, upsert_document, \
    upsert_document_embedding, upsert_document_summary, SearchResult
from sbretrieval.exceptions import DocumentIndexingError, DocumentRemovalError, DocumentSearchError


async def index_document(
    connection: Connection,
    document_key: str,
    document_content: str,
    ai_vendor: str,
    embedding_model: str,
    summary_model: str,
    summary_prompt: str,
    document_secondary_key: Optional[str] = None,
) -> None:
    '''
    Takes a document key and content, count the tokens of the content, generates a summary, generates an
    embedding of the summary, and save both the received and generated data.
    '''

    try:
        # checking the given parameters
        assert connection, 'Connection was not provided.'
        assert document_key, 'Document key was not provided.'
        assert document_content, 'Document content was not provided.'
        assert ai_vendor, 'AI vendor was not provided.'
        assert embedding_model, 'Embedding model was not provided.'
        assert summary_model, 'Summary model was not provided.'
        assert summary_prompt, 'Summary prompt was not provided.'

        # loading the AI module according to the AI vendor string
        ai_module = load_module_by_vendor(ai_vendor)

        # getting the token count for the document content
        document_token_count = await ai_module.count_tokens(document_content, summary_model)

        # requesting a summary of the document to the LLM
        formatted_prompt = summary_prompt.format(document_content)
        document_summary = await ai_module.send_prompt(formatted_prompt, summary_model)

        # generating an embedding for the summary
        document_embedding = await ai_module.generate_embedding(document_summary, embedding_model)

        # upserting everything we generated into the database
        async with connection.transaction():

            await upsert_document(connection, document_key, document_token_count, document_secondary_key)

            await upsert_document_summary(
                connection, document_key, document_summary, ai_vendor, summary_model
            )

            await upsert_document_embedding(
                connection, document_key, document_embedding, ai_vendor, embedding_model
            )

    except Exception as e:

        # re-raising the error with the library's own exception type
        raise DocumentIndexingError() from e


async def remove_document(connection: Connection, document_key: str) -> bool:
    '''
    Removes from the database all indexed information from the given document.
    Returns true if all the database records were found and deleted and false if any of them were missing.
    '''

    try:

        # checking the given parameters
        assert connection, 'Connection was not provided.'
        assert document_key, 'Document key was not provided.'

        # deletes all records from all tables related to this document key
        async with connection.transaction():
            return await delete_document(connection, document_key)

    except Exception as e:

        # re-raising the error with the library's own exception type
        raise DocumentRemovalError() from e


async def search_documents(
    connection: Connection,
    query: str,
    max_token_count: int,
    ai_vendor: str,
    embedding_model: str,
    document_secondary_key: Optional[str] = None,
) -> SearchResult:
    '''
    Takes a query and generates an embedding of it, then searches for similar documents (by embedding
    proximity).
    '''

    try:
        # checking the given parameters
        assert connection, 'Connection was not provided.'
        assert query, 'Query was not provided.'
        assert max_token_count > 0, 'Max token count should be a positive integer.'
        assert ai_vendor, 'AI vendor was not provided.'
        assert embedding_model, 'Embedding model was not provided.'

        # loading the AI module according to the AI vendor string
        ai_module = load_module_by_vendor(ai_vendor)

        # generating an embedding for the summary
        document_embedding = await ai_module.generate_embedding(query, embedding_model)

        # performing the embedding search on the database and returning the results
        async with connection.transaction():
            return await search_documents_by_embeddings(
                connection, document_embedding, max_token_count, document_secondary_key
            )

    except Exception as e:

        # re-raising the error with the library's own exception type
        raise DocumentSearchError() from e
