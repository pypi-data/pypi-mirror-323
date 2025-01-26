# dkgr_client

## Installation

```bash
pip install dkgr_client
```

## Usage

```python
from dkgr_client import ValidationClient

try:
    # Initialize the client
    client = ValidationClient(
        api_key='your_api_key', 
        base_url='https://api.example.com'
    )
    
    # Start a new event
    client.start_event()

    # Validate
    results = client.validate(
        type,
        text,
    )

    # Extract useful info from results
    client.humaize_response(results))

    # Close the client
    client.close()

except Exception as e:
    print(e)
```
