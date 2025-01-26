# rustme/__init__.py

from .ame_chunk import ame_chunk
from rustme_rust import ame as ame_rust  # Updated to import from 'rustme_rust'

__all__ = ['ame_rust', 'ame_chunk']
