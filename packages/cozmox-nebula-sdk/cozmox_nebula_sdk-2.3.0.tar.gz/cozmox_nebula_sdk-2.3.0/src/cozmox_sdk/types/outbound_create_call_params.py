# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["OutboundCreateCallParams"]


class OutboundCreateCallParams(TypedDict, total=False):
    agent_id: Required[Annotated[str, PropertyInfo(alias="agentId")]]
    """Agent ID which will communicate with user"""

    extras: Required[object]
    """Extra parameters needed for agent on call"""

    from_phone: Required[Annotated[str, PropertyInfo(alias="fromPhone")]]
    """From phone number"""

    to_phone: Required[Annotated[str, PropertyInfo(alias="toPhone")]]
    """The phone number to call"""
