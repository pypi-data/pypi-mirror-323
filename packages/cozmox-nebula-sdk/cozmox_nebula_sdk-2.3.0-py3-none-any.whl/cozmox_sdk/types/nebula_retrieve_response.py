# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from .._models import BaseModel

__all__ = ["NebulaRetrieveResponse"]


class NebulaRetrieveResponse(BaseModel):
    consumed_concurrency: float
    """The amount of concurrency consumed"""
