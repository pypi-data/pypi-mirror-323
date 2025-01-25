# Cereale SDK

[Bursa de cereale](https://bursadecereale.com) facilitează conexiunea directă între fermieri și cumpărători, eliminând intermediarii. Permite publicarea anunțurilor și, prin SDK, asigură integrarea și comunicarea ușoară cu platforma.



## Installation

```bash
pip install cereale-sdk
```

## Usage

```python
from cereale_sdk import CerealeClient

client = CerealeClient()
client.verify(phone="+40722111222", code="0000")

# Get listings
listings = client.get_listings(category="porumb")
```

## Features

- Complete API coverage
- Authentication handling
- File upload support
- Error handling