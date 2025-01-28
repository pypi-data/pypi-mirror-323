"""JAX API Utility Package."""

from importlib import metadata
import importlib.util

__version__ = metadata.version("jax-apiutils")

fastapi_spec = importlib.util.find_spec("fastapi")

if fastapi_spec is not None:
    from jax.apiutils.fastapi import *

pydantic_spec = importlib.util.find_spec("pydantic")

if pydantic_spec is not None:
    from jax.apiutils.schemas.pydantic import *
else:
    from jax.apiutils.schemas.dataclasses import *
