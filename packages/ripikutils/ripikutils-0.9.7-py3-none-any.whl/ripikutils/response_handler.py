import json
import numpy as np
import typesentry
import warnings


class NpEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that extends json.JSONEncoder to handle NumPy data types.
    
    This encoder converts NumPy data types to their Python equivalents, making them
    JSON serializable. It handles numpy integers, floats, arrays, complex numbers,
    booleans, and void types.
    """
    def default(self, obj):
        """
        Convert NumPy data types to JSON serializable Python types.

        Args:
            obj: The object to be serialized to JSON.

        Returns:
            The Python equivalent of the NumPy data type:
            - NumPy integers -> Python int
            - NumPy floats -> Python float
            - NumPy arrays -> Python list
            - NumPy complex numbers -> dict with 'real' and 'imag' keys
            - NumPy booleans -> Python bool
            - NumPy void -> None
            
        Examples:
            >>> import json
            >>> import numpy as np
            >>> data = {'array': np.array([1, 2, 3]), 'number': np.float64(1.5)}
            >>> json.dumps(data, cls=NpEncoder)
            '{"array": [1, 2, 3], "number": 1.5}'
        """

        if isinstance(obj, np.integer):
            return int(obj)

        if isinstance(obj, np.floating):
            return float(obj)

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        if isinstance(obj, (np.bool_)):
            return bool(obj)

        if isinstance(obj, (np.void)):
            return None

        return super(NpEncoder, self).default(obj)


def sanitize_numpy_dict(dictionary: dict):
    """
    Convert a dictionary containing NumPy objects to a pure Python dictionary.

    This function takes a dictionary that may contain NumPy data types (such as 
    np.array, np.float64, etc.) and converts it to a dictionary with only standard 
    Python objects. It achieves this by performing a JSON serialization and 
    deserialization using the NpEncoder class.

    Args:
        dictionary (dict): Input dictionary that may contain NumPy objects.

    Returns:
        dict: A new dictionary with all NumPy objects converted to their Python equivalents:
            - NumPy arrays -> Python lists
            - NumPy integers -> Python int
            - NumPy floats -> Python float
            - NumPy complex numbers -> dict with 'real' and 'imag' keys
            - NumPy booleans -> Python bool
            - NumPy void -> None

    Examples:
        >>> import numpy as np
        >>> data = {'array': np.array([1, 2, 3]), 'value': np.float64(1.5)}
        >>> result = sanitize_numpy_dict(data)
        >>> print(result)
        {'array': [1, 2, 3], 'value': 1.5}
    """
    
    json_object = json.dumps(dictionary, cls = NpEncoder, indent=4)
    return json.loads(json_object)


def verify_response_mapping(response: dict, expected_kv_mapping: dict):
    """
    Verify if the response dictionary matches the expected key-value mapping.
    Args:
        response (dict): Response dictionary to verify
        expected_kv_mapping (dict): Expected key-value mapping
    Returns:
        bool: True if the response matches the expected key-value
    """
    if not isinstance(response, dict):
        warnings.warn("ResponseTypeMismatch: Response must be a dictionary.")
        return False
    if not isinstance(expected_kv_mapping, dict):
        warnings.warn("ExpectedKVMappingMismatch: Expected key-value mapping must be a dictionary.")
        return False
    resp_keys = response.keys()
    expected_keys = expected_kv_mapping.keys()
    if not set(resp_keys) == set(expected_keys):
        warnings.warn(f"KeysMismatch: Expected keys {expected_keys} but found {resp_keys}.")
        return False
    is_typed = typesentry.Config(soft_exceptions=False).is_type
    for k, v in response.items():
        if not is_typed(v, expected_kv_mapping[k]):
            warnings.warn(f"KeyDtypeMismatch: Expected type {expected_kv_mapping[k]} but found type mismatch for key '{k}'.")
            return False
    return True