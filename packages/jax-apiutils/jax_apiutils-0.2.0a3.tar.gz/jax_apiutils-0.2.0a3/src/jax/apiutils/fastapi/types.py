from datetime import date
from typing import Annotated, Optional

from fastapi import Query

from jax.apiutils.fastapi.schemas.const.messages import (
    CHECK_DB_HEALTH,
    CREATE_DATE,
    INT,
    LIMIT,
    OFFSET,
    SEARCH_TEXT,
    UPDATE_DATE,
)

_IntQuery = Query(
    format="int64", minimum=0, maxiumum=9223372036854775807, description=INT
)
Int = Annotated[int, _IntQuery]
OptionalInt = Annotated[Optional[int], _IntQuery]

_LimitIntQuery = Query(
    format="int64",
    minimum=0,
    maxiumum=1000,
    description=LIMIT,
)
LimitInt = Annotated[int, _LimitIntQuery]
OptionalLimitInt = Annotated[Optional[int], _LimitIntQuery]

_OffsetIntQuery = Query(
    format="int64",
    minimum=0,
    maxiumum=9223372036854775807,
    description=OFFSET,
)
OffsetInt = Annotated[int, _OffsetIntQuery]
OptionalOffsetInt = Annotated[Optional[int], _OffsetIntQuery]

_SearchTextQuery = Query(description=SEARCH_TEXT)
SearchText = Annotated[str, _SearchTextQuery]
OptionalSearchText = Annotated[Optional[str], _SearchTextQuery]

_CheckDbHealthQuery = Query(description=CHECK_DB_HEALTH)
CheckDbHealth = Annotated[bool, _CheckDbHealthQuery]
OptionalCheckDbHealth = Annotated[Optional[bool], _CheckDbHealthQuery]

_CreateDateQuery = Query(description=CREATE_DATE)
CreateDate = Annotated[date, _CreateDateQuery]
OptionalCreateDate = Annotated[Optional[date], _CreateDateQuery]

_UpdateDateQuery = Query(description=UPDATE_DATE)
UpdateDate = Annotated[date, _UpdateDateQuery]
OptionalUpdateDate = Annotated[Optional[date], _UpdateDateQuery]
