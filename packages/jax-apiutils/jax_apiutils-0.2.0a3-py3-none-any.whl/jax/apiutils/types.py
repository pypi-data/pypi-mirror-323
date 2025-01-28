"""Type aliases for JAX API utilities."""

import importlib.util

fastapi_spec = importlib.util.find_spec("fastapi")
if fastapi_spec is not None:
    from jax.apiutils.fastapi.types import *
