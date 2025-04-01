# proxmox-client
[![PyPI Version](https://img.shields.io/pypi/v/proxmox-client)](https://pypi.org/project/proxmox-client)

Python client for Proxmox

## Installation
```bash
pip install proxmox-client
```

## Examples
### Create class
```python
from proxmox_client import ProxmoxClient
proxmox = ProxmoxClient( "PROXMOX_DOMAIN", "PROXMOX_USER", "PROXMOX_PASSWORD" )
```
where:
- PROXMOX_DOMAIN: URL of Proxmox WebUi page
- PROXMOX_USER: User of Proxmox WebUi
- PROXMOX_PASSWORD: Password of Proxmox WebUi

or using environment variables "PROXMOX_DOMAIN" and "PROXMOX_USER" and "PROXMOX_PASSWORD":
```python
from dotenv import load_dotenv
import os
from proxmox_client import ProxmoxClient
load_dotenv()

def main():
    proxmox = ProxmoxClient( 
        base_url=os.getenv('PROXMOX_DOMAIN'), 
        login=os.getenv('PROXMOX_USER'),
        password=os.getenv('PROXMOX_PASSWORD')
    )

    print( proxmox.get(1) )
if __name__ == "__main__":
    main() 