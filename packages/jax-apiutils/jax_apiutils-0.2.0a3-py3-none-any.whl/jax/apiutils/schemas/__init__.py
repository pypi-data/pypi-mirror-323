"""JAX API schemas."""

import importlib.util

pydantic_spec = importlib.util.find_spec("pydantic")

if pydantic_spec is not None:
    from jax.apiutils.schemas.pydantic import *

from . import dataclasses as dataclasses
