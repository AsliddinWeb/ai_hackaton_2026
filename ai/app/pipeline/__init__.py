"""Tasvir quvuri: foto -> modelga tayyor tasvir."""

from .detect import Quad, find_film
from .normalize import Normalized, normalize
from .quality import Quality, assess

__all__ = ["Quad", "find_film", "Normalized", "normalize", "Quality", "assess"]
