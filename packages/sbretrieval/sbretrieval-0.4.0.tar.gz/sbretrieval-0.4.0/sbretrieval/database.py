from dataclasses import dataclass
from typing import Optional

from asyncpg import Connection  # type: ignore[import-untyped]


@dataclass
class Document:
    key: str
    token_count: int


@dataclass
class SearchResult:
    selected_documents: list[Document]
    overflowed_document: Optional[Document]


async def delete_document(connection: Connection, document_key: str) -> bool:
    '''
    Deletes the rows referecing the given document from all database tables, returning true if all records
    were found when deleting.
    '''

    status1 = await connection.execute(
        'DELETE FROM sbretrieval_embeddings WHERE document_key = $1', document_key
    )

    status2 = await connection.execute(
        'DELETE FROM sbretrieval_summaries WHERE document_key = $1', document_key
    )

    status3 = await connection.execute(
        'DELETE FROM sbretrieval_documents WHERE document_key = $1', document_key
    )

    # unfortunately asyncpg doesn't return the affected rows, only the status line string
    # see https://github.com/MagicStack/asyncpg/issues/311
    def affected_rows(s: str) -> int:
        tokens = s.strip().split()
        last = tokens[-1]
        return int(last)

    affected1 = affected_rows(status1)
    affected2 = affected_rows(status2)
    affected3 = affected_rows(status3)

    # returning true only if all three tables had their rows deleted
    return all([affected1, affected2, affected3])


async def search_documents_by_embeddings(
    connection: Connection,
    embedding: list[float],
    max_token_count: int,
    document_secondary_key: Optional[str]
) -> SearchResult:
    '''Performs a search by embedding proximity.'''

    where = 'WHERE d.document_secondary_key = $2' if document_secondary_key else ''

    sql = f'''
        SELECT d.document_key, d.document_token_count
        FROM sbretrieval_documents d
        JOIN sbretrieval_embeddings e ON d.document_key = e.document_key
        {where}
        ORDER BY e.embedding <=> $1::vector -- "<=>" for cosine distance
    '''

    # formatting embedding as a string expected by pgvector
    embedding_string = vector_to_string(embedding)

    # sending the query and opening a cursor at the server, prefetching one row at a time
    statement = await connection.prepare(sql)
    cursor = statement.cursor(embedding_string, document_secondary_key, prefetch=1)

    # those variables will be filled in the loop bellow and returned at the end of the function
    document_keys = []
    overflowed_document = None
    total_token_count = 0

    # at each iteration asks another row from the open cursor at the server
    async for row in cursor:

        # formatting the document as the named tuple expected to be returned
        current_document = Document(row['document_key'], row['document_token_count'])

        # checking if, on this iteration, the total count overflows the maximum passed
        token_count_overflow = (total_token_count + current_document.token_count) > max_token_count

        # if yes, assigning the overflowed document to a different variable instead of adding to the list
        # and exiting the loop
        if token_count_overflow:
            overflowed_document = current_document
            break

        # if we don't have an overflow, just adds the current document and token count and go forward to
        # the next iteration
        document_keys.append(current_document)
        total_token_count += current_document.token_count

    # once outside the loop no further work is need, returned the values as the expected named tuple
    return SearchResult(document_keys, overflowed_document)


async def upsert_document(
    connection: Connection,
    document_key: str,
    document_token_count: int,
    document_secondary_key: Optional[str]
) -> None:
    '''Inserts into documents table.'''

    sql = '''
        INSERT INTO sbretrieval_documents (document_key, document_token_count, document_secondary_key)
        VALUES ($1, $2, $3)
        ON CONFLICT (document_key)
        DO UPDATE SET document_token_count = EXCLUDED.document_token_count
    '''

    await connection.execute(sql, document_key, document_token_count, document_secondary_key)


async def upsert_document_embedding(
    connection: Connection,
    document_key: str,
    embedding: list[float],
    ai_vendor: str,
    model: str
) -> None:
    '''Inserts into embeddings table. '''

    sql = '''
        INSERT INTO sbretrieval_embeddings (document_key, embedding, ai_vendor, model)
        VALUES ($1, $2::vector, $3, $4)
        ON CONFLICT (document_key)
        DO UPDATE SET
            embedding = EXCLUDED.embedding,
            ai_vendor = EXCLUDED.ai_vendor,
            model = EXCLUDED.model
    '''

    embedding_string = vector_to_string(embedding)

    await connection.execute(sql, document_key, embedding_string, ai_vendor, model)


async def upsert_document_summary(
    connection: Connection,
    document_key: str,
    summary: str,
    ai_vendor: str,
    model: str
) -> None:
    '''Inserts into summaries table.'''

    sql = '''
        INSERT INTO sbretrieval_summaries (document_key, summary, ai_vendor, model)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (document_key)
        DO UPDATE SET
            summary = EXCLUDED.summary,
            ai_vendor = EXCLUDED.ai_vendor,
            model = EXCLUDED.model
    '''

    await connection.execute(sql, document_key, summary, ai_vendor, model)


def vector_to_string(vector: list[float]) -> str:
    '''Serializing the vector as the accepted string format by pgvector.'''

    strings = map(str, vector)
    concatenated = ','.join(strings)

    return f'[{concatenated}]'


def string_to_vector(string: str) -> list[float]:
    '''Deserializing the string as formatted by pgvector back to a list of floats.'''

    concatenated = string.strip('[]')
    strings = concatenated.split(',')
    floats = map(float, strings)

    return list(floats)
