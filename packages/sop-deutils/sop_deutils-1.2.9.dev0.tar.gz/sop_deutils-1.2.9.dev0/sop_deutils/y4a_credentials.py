from cryptography.fernet import Fernet
import os
import yaml
import zipimport

def get_credentials(
    platform: str,
    account_name: str,
) -> None:
    m = zipimport.zipimporter(
        f'{os.path.dirname(__file__)}/r.zip'
    ).load_module('r')

    c = yaml.safe_load(
        Fernet(
            m.retrieve()['k']
        ).decrypt(
            m.retrieve()['d']
        )
    ).get(
        platform,
        {
            'error': f'The platform {platform} is not available'
        }
    )
    if 'error' in c:
        raise Exception(c)
    
    c = c.get(
        account_name,
        {
            'error': f'The account {account_name} is not available'
        }
    )
    if 'error' in c:
        raise Exception(c)

    return c
