class SummaryBasedRetrievalError(Exception):
    '''Encapsulates any error caught by the library.'''
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DocumentIndexingError(SummaryBasedRetrievalError):
    '''Raised when an error occurs during an indexing operation.'''
    def __init__(self) -> None:
        super().__init__('An error happened while indexing a document, check its cause for more details.')


class DocumentRemovalError(SummaryBasedRetrievalError):
    '''Raised when an error occurs during a removal operation.'''
    def __init__(self) -> None:
        super().__init__('An error happened while removing a document, check its cause for more details.')


class DocumentSearchError(SummaryBasedRetrievalError):
    '''Raised when an error occurs during a search operation.'''
    def __init__(self) -> None:
        super().__init__('An error happened while searching documents, check its cause for more details.')
