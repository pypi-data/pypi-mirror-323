import os
import sys
import chardet

def env_or_die(name: str) -> str:
    """Retrieve an environment variable or exit the script with an error message if it's not set."""
    value = os.getenv(name)
    if value is None:
        print(f"Error: Required environment variable '{name}' is not set.", file=sys.stderr)
        sys.exit(1)
    return value

def to_utf8(raw_data: bytes | bytearray) -> str:
    """
    Converts raw byte data to UTF-8 encoding if it is not already UTF-8.

    Parameters:
    - raw_data (bytes | bytearray): The raw byte content of a file or other datasource.

    Returns:
    - string: The content transcoded to UTF-8.
    """
    # Detect the encoding
    result = chardet.detect(raw_data)
    source_encoding = result.get('encoding')

    if not source_encoding:
        raise ValueError("Encoding could not be detected.")
    
    # Check if the data is already UTF-8 encoded
    if source_encoding.lower() == 'utf-8':
        return raw_data
    
    try:
        # Decode with the detected encoding and encode to UTF-8
        return raw_data.decode(source_encoding, errors='replace') #.encode('utf-8')
    except (LookupError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to decode or encode data: {e}")