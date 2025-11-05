import os


def _get_secret_from_environment(name: str) -> str:
    secret = os.environ.get(name, '').strip()

    if secret:
        print(f'✅ Environment Variable: Found {name}')
        return secret

    print(f'❌ Environment Variable : {name} is not set')

    try:
        from google.colab import userdata

        secret = userdata.get(name)
        print(f'✅ Google Colab: Found {name}')
    except Exception as e:
        print(f'❌ Google Colab: {e}')

    return secret.strip()


def _get_secret_from_user(name: str) -> str:
    from getpass import getpass

    return getpass(f'Enter the secret value for {name}: ')


def get_secret(name: str) -> str:
    secret = _get_secret_from_environment(name)
    if not secret:
        secret = _get_secret_from_user(name)

    return secret
