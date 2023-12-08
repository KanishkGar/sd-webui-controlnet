import importlib.util
import os
import pkg_resources
from typing import Tuple, Optional

req_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
default_command_live = (os.environ.get('WEBUI_LAUNCH_LIVE_OUTPUT') == "1")
index_url = os.environ.get('INDEX_URL', "")


def run_pip(command, desc=None, live=default_command_live):
    index_url_line = f' --index-url {index_url}' if index_url != '' else ''
    return run(f'"{python}" -m pip {command} --prefer-binary{index_url_line}', desc=f"Installing {desc}", errdesc=f"Couldn't install {desc}", live=live)


def is_installed(package):
    try:
        spec = importlib.util.find_spec(package)
    except ModuleNotFoundError:
        return False

    return spec is not None
    

def comparable_version(version: str) -> Tuple:
    return tuple(version.split('.'))
    

def get_installed_version(package: str) -> Optional[str]:
    try:
        return pkg_resources.get_distribution(package).version
    except Exception:
        return None


with open(req_file) as file:
    for package in file:
        try:
            package = package.strip()
            if '==' in package:
                package_name, package_version = package.split('==')
                installed_version = get_installed_version(package_name)
                if installed_version != package_version:
                    run_pip(f"install -U {package}", f"sd-webui-controlnet requirement: changing {package_name} version from {installed_version} to {package_version}")
            elif '>=' in package:
                package_name, package_version = package.split('>=')
                installed_version = get_installed_version(package_name)
                if not installed_version or comparable_version(installed_version) < comparable_version(package_version):
                    run_pip(f"install -U {package}", f"sd-webui-controlnet requirement: changing {package_name} version from {installed_version} to {package_version}")
            elif not is_installed(package):
                run_pip(f"install {package}", f"sd-webui-controlnet requirement: {package}")
        except Exception as e:
            print(e)
            print(f'Warning: Failed to install {package}, some preprocessors may not work.')
