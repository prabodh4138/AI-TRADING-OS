"""
=========================================================
AI Trading OS

Unit Tests
Response Validator
=========================================================
"""

from requests.models import Response
import pytest

from data_engine.validator.response_validator import ResponseValidator
from data_engine.exceptions import DownloadException


def make_response(
    status: int = 200,
    text: str | None = None,
) -> Response:
    """
    Create a fake HTTP response for testing.

    If no text is supplied, generate a realistic CSV
    similar in size to an NSE Bhavcopy.
    """

    if text is None:

        header = "SYMBOL,OPEN,HIGH,LOW,CLOSE,VOLUME\n"

        rows = []

        for i in range(25):
            rows.append(
                f"ABC{i},100,101,99,100.5,{10000+i}"
            )

        text = header + "\n".join(rows)

    response = Response()
    response.status_code = status
    response._content = text.encode("utf-8")

    return response


# =====================================================
# VALID RESPONSE
# =====================================================

def test_valid_response():

    validator = ResponseValidator(
        required_header="SYMBOL"
    )

    assert validator.validate(
        make_response()
    )


# =====================================================
# INVALID STATUS
# =====================================================

def test_invalid_status():

    validator = ResponseValidator(
        required_header="SYMBOL"
    )

    with pytest.raises(
        DownloadException
    ):
        validator.validate(
            make_response(status=404)
        )


# =====================================================
# EMPTY RESPONSE
# =====================================================

def test_empty_response():

    validator = ResponseValidator(
        required_header="SYMBOL"
    )

    with pytest.raises(
        DownloadException
    ):
        validator.validate(
            make_response(text="")
        )


# =====================================================
# HTML RESPONSE
# =====================================================

def test_html_response():

    validator = ResponseValidator(
        required_header="SYMBOL"
    )

    with pytest.raises(
        DownloadException
    ):
        validator.validate(
            make_response(
                text="<html>Error</html>"
            )
        )


# =====================================================
# MISSING HEADER
# =====================================================

def test_missing_header():

    validator = ResponseValidator(
        required_header="SYMBOL"
    )

    with pytest.raises(
        DownloadException
    ):
        validator.validate(
            make_response(
                text="ABC,100,101"
            )
        )