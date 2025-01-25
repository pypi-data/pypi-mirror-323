# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["LamIntegrationRunParamsBase", "LamIntegrationRunParamsNonStreaming", "LamIntegrationRunParamsStreaming"]


class LamIntegrationRunParamsBase(TypedDict, total=False):
    raccoon_passcode: Required[str]
    """
    The raccoon passcode associated with the end user on behalf of which the call is
    being made.
    """

    integration_id: Optional[str]
    """The unique identifier for the integration being called."""

    properties: Optional[object]
    """Additional properties or data related to the particular integration."""


class LamIntegrationRunParamsNonStreaming(LamIntegrationRunParamsBase, total=False):
    stream: Optional[Literal[False]]
    """Whether the response should be streamed back or not."""


class LamIntegrationRunParamsStreaming(LamIntegrationRunParamsBase):
    stream: Required[Literal[True]]
    """Whether the response should be streamed back or not."""


LamIntegrationRunParams = Union[LamIntegrationRunParamsNonStreaming, LamIntegrationRunParamsStreaming]
