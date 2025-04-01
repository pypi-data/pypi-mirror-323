from importlib import import_module
from types import ModuleType


def load_module_by_vendor(ai_vendor: str) -> ModuleType:
    '''Dynamically loads the AI module according to the AI vendor string and returns it.'''

    try:
        return import_module(f'sbretrieval.ai_models.{ai_vendor}')

    except ModuleNotFoundError:
        raise ValueError(f'Invalid AI vendor: {ai_vendor}')
