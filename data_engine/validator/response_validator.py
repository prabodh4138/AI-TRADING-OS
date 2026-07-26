"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    response_validator.py

Purpose
-------
Validate HTTP responses returned by download providers.

Responsibilities
----------------
1. Validate HTTP status code
2. Validate response content
3. Detect HTML/error pages
4. Validate required header
5. Validate minimum content size

This validator is provider-independent.

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

from requests import Response

from ..exceptions import DownloadException


class ResponseValidator:
    """
    Generic HTTP response validator.

    This class validates downloaded content before it
    is saved to disk.
    """

    def __init__(
        self,
        required_header: str,
        minimum_size: int = 100,
    ) -> None:
        """
        Parameters
        ----------
        required_header
            Expected header in the response.

        minimum_size
            Minimum acceptable response size.
        """

        self.required_header = required_header
        self.minimum_size = minimum_size

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def validate(
        self,
        response: Response,
    ) -> bool:
        """
        Validate downloaded response.

        Raises
        ------
        DownloadException
            If validation fails.
        """

        self._validate_status(response)

        self._validate_empty(response)

        self._validate_html(response)

        self._validate_size(response)

        self._validate_header(response)

        return True

    # --------------------------------------------------
    # Individual Validation Steps
    # --------------------------------------------------

    def _validate_status(
        self,
        response: Response,
    ) -> None:

        if response.status_code != 200:

            raise DownloadException(
                f"HTTP {response.status_code}"
            )

    def _validate_empty(
        self,
        response: Response,
    ) -> None:

        if not response.text:

            raise DownloadException(
                "Response is empty."
            )

    def _validate_html(
        self,
        response: Response,
    ) -> None:

        text = response.text.lstrip().lower()

        if text.startswith("<html"):

            raise DownloadException(
                "HTML received instead of CSV."
            )

    def _validate_size(
        self,
        response: Response,
    ) -> None:

        if len(response.text) < self.minimum_size:

            raise DownloadException(
                "Response content is too small."
            )

    def _validate_header(
        self,
        response: Response,
    ) -> None:

        if self.required_header not in response.text:

            raise DownloadException(
                f"Missing required header: "
                f"{self.required_header}"
            )