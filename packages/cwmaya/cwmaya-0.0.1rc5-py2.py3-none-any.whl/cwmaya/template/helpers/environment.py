
def composeEnvVars(env_vars):
    """
    Processes a list of environment variables and composes a dictionary of key-value pairs.

    The function handles keys both with and without square brackets:
    - If a key is enclosed in square brackets and already exists in the result dictionary,
    the new value is concatenated to the existing value using a colon as a separator.
    - If a key is enclosed in square brackets and does not exist in the result dictionary,
    it is added without the brackets.
    - If a key is not enclosed in brackets, it is added to the dictionary directly, and any
    existing value under the same key is overwritten.

    Args:
        env_vars (list of dict): A list of dictionaries where each dictionary has a 'key' and 'value'
                                indicating the environment variable's name and value respectively.

    Returns:
        dict: A dictionary with environment variable keys as dictionary keys and the corresponding values.
            If keys are enclosed in brackets and repeated, their values are concatenated.

    Example:
        >>> composeEnvVars([{"key": "[PATH]", "value": "/usr/bin"}, {"key": "[PATH]", "value": "/bin"}])
        {'PATH': '/usr/bin:/bin'}
        >>> composeEnvVars([{"key": "USER", "value": "root"}, {"key": "SHELL", "value": "/bin/bash"}])
        {'USER': 'root', 'SHELL': '/bin/bash'}
    """
    result = {}
    for env_var in env_vars:
        key = env_var["key"]
        value = env_var["value"]

        if key.startswith("[") and key.endswith("]"):
            stripped_key = key[1:-1]
            if stripped_key in result:
                result[stripped_key] = f"{result[stripped_key]}:{value}"
            else:
                result[stripped_key] = value
        else:
            result[key] = value

    return result
