from thinknet_application_specific_exception import BaseErrorData


class ErrorData(BaseErrorData):
    UTV01 = (ValueError, 11, "Input must not be empty or contain only whitespace after stripping.")
    UTV02 = (ValueError, 12, "Input has an invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM).")
    UTV03 = (ValueError, 13, "Invalid format must match '%Y-%m-%dT%H:%M:%SZ'.")
    UTT01 = (TypeError, 21, "Input must be string type.")
    UTO01 = (OverflowError, 31, "milliseconds out of range for platform time_t. The value is too large for conversion.")
    UTX99 = (Exception, 99, "Unspecified or unexpected errors.")
