from datetime import datetime
import pytz
from thinknet_application_specific_exception import raise_error
from thinknet_variable_validator.error_data import ErrorData


def convert_millis_to_datetime(millis: float) -> str:
    try:
        seconds = millis / 1000.0
        utc_time = datetime.fromtimestamp(seconds, pytz.UTC)
        thailand_tz = pytz.timezone("Asia/Bangkok")
        thailand_time = utc_time.astimezone(thailand_tz)
        formatted_time = thailand_time.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise_error(ErrorData.UTV04, {"millis": millis})
    return formatted_time


def validate_and_strip_str_variable(value: str) -> str:
    if not isinstance(value, str):
        raise_error(ErrorData.UTT01, {"value": value})
    value_stripped = value.strip()
    if not value_stripped:
        raise_error(ErrorData.UTV01, {"value": value, "value_stripped": value_stripped})
    return value_stripped


def validate_and_parse_to_datetime(value: str) -> datetime:
    value_stripped = validate_and_strip_str_variable(value)

    try:
        parsed_datetime = datetime.strptime(value_stripped, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        raise_error(
            ErrorData.UTV02,
            {"value": value, "value_stripped": value_stripped},
        )
    return parsed_datetime


def validate_and_check_format_datetime(value: str) -> str:
    value_stripped = validate_and_strip_str_variable(value)

    try:
        datetime.strptime(value_stripped, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        raise_error(ErrorData.UTV03, {"value": value, "value_stripped": value_stripped})
    return value_stripped
