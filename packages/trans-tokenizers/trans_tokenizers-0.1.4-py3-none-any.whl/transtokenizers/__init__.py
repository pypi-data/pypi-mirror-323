"""Top-level package for transtokenizers."""

__author__ = """Pieter Delobelle, François Remy"""
__email__ = 'pieter.delobelle@kuleuven.be, francois.remy@ugent.be'
__version__ = '0.1.4'

from .transtokenizers import align, create_aligned_corpus, map_tokens, remap_model, smooth_mapping
