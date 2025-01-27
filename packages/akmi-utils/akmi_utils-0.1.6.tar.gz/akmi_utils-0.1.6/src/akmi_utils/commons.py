import os
import tomli

def get_project_details(base_dir: str, keys: list):
    with open(os.path.join(base_dir, 'pyproject.toml'), 'rb') as file:
        package_details = tomli.load(file)
    poetry = package_details['project']
    return {key: poetry[key] for key in keys}
