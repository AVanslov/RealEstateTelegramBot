async def max_value_validation_error(value, min_value):
    return value.isdigit() and int(value) >= int(min_value) and (
        int(value) < 2147483647
    )
