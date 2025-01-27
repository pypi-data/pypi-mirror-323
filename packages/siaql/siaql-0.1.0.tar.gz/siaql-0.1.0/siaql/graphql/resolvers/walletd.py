# siaql/graphql/resolvers/walletd.py
from dataclasses import fields
from typing import Any, Dict, Optional, TypeVar, Callable, get_origin, get_args
from strawberry.types import Info
from typing import Any, Dict, Optional, TypeVar, Callable, Type, get_type_hints, List
from strawberry.types import Info
import inspect
from functools import wraps

# from strawberry.types import StrawberryList
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin
from dataclasses import fields
import strawberry
from strawberry.types.base import StrawberryList, StrawberryType, StrawberryOptional
from strawberry.types.scalar import ScalarWrapper, ScalarDefinition
from strawberry.types.enum import EnumDefinition as StrawberryEnum
from strawberry.types.union import StrawberryUnion

from strawberry.types.lazy_type import LazyType
from strawberry.exceptions import MissingTypesForGenericError
from siaql.graphql.resolvers.converter import TypeConverter
from datetime import datetime
from siaql.graphql.resolvers.filter import FilterInput, SortInput, PaginationInput, QueryFiltering

import inspect
import enum
import logging

from datetime import datetime

logger = logging.getLogger("siaql.resolvers.walletd")

T = TypeVar("T")


class WalletdBaseResolver:
    """Base resolver class for Walletd API"""

    @classmethod
    async def handle_api_call(
        cls,
        info: Info,
        method: str,
        transform_func: Optional[Callable[[Dict], T]] = None,
        filter_input: Optional[FilterInput] = None,
        sort_input: Optional[SortInput] = None,
        pagination_input: Optional[PaginationInput] = None,
        *args,
        **kwargs,
    ) -> Any:
        """Generic method to handle API calls with error handling"""
        # Check if endpoint is skipped
        if info.context["skipped_endpoints"].get("walletd", False):
            raise Exception("Walletd endpoint was skipped during startup. This query is not available.")

        client = info.context["walletd_client"]
        method_func = getattr(client, method)
        try:

            # 1. Get raw data from API
            result = await method_func(*args, **kwargs)
            logger.debug("Executing method: %s", method_func)

            # 2. Apply any custom transformations
            if transform_func:
                result = transform_func(result)

            # 3. Convert to proper GraphQL types if this is a typed field
            if hasattr(info, "_field"):
                field_type = info._field.type
                # Convert the entire result to proper GraphQL types
                result = TypeConverter.convert(result, field_type)
            # 4. Apply filtering, sorting, and pagination AFTER type conversion
            if isinstance(result, list):
                if filter_input:
                    # Now the data is in proper GraphQL types, making it easier to filter
                    result = QueryFiltering.apply_filter(result, filter_input)
                if sort_input:
                    result = QueryFiltering.apply_sort(result, sort_input)
                if pagination_input:
                    result = QueryFiltering.apply_pagination(result, pagination_input)
            return result
        except Exception as e:
            logger.error("Error in handle_api_call: %s", e)
            raise e
