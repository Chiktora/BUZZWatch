def validate_input(data, required_keys):
    """
    Validates input data for required keys.
    """
    missing_keys = [key for key in required_keys if key not in data]
    return missing_keys
