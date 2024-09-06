import os
import site
import sys
import subprocess
import argparse

exe_name = "mobiledevice3"
upx_dir = ''

os.chdir(os.path.dirname(os.path.abspath(__file__)))
iswin = sys.platform.startswith('win')


parser = argparse.ArgumentParser(description='Command Line Parser')
parser.add_argument('--onedir', action='store_true')
parser.add_argument('--name', default='mobiledevice')
parser.add_argument('--venv', action='store_true')
args = parser.parse_args()

# run in virtual environment
if args.venv:
    env_name = "venv"
    if not sys.prefix.endswith(env_name):
        print("switch to virtual environment")
        if not os.path.exists(env_name):
            # if wndows
            if iswin:
                os.system(f"python -m venv {env_name}")
            else:
                os.system(f"python3 -m venv {env_name}")
        if iswin:
            python_executable = os.path.join(env_name, 'Scripts', 'python.exe')
        else:
            python_executable = os.path.join(env_name, 'bin', 'python')
        print(f"run: {python_executable} {sys.argv}")
        subprocess.run([python_executable, *sys.argv])
        sys.exit(0)


# install required packages
if iswin:
    os.system("pip install -r requirements.txt")
    os.system("pip install pyinstaller")
    os.system("pip install apple-compress")
else:
    os.system("pip3 install -r requirements.txt")
    os.system("pip3 install pyinstaller")
    os.system("pip3 install apple-compress")

import PyInstaller.__main__

for file in site.getsitepackages():
    if file.endswith("site-packages"):
        site_packages_path = file
        break
print(f"site_packages_path:{site_packages_path}")

resources_dir = os.path.join(".", "pymobiledevice3", "resources")
pymobiledevice3_cli_path = os.path.join(".", "pymobiledevice3", "cli")

hidden_imports = []
for module in os.listdir(pymobiledevice3_cli_path):
    if module.endswith(".py") and module != "init.py":  # Avoid including the init.py
        # Create the module name to be added to hidden imports
        module_name = (
            "pymobiledevice3.cli." + module[:-3]
        )  # Strip off '.py' from the file name
        hidden_imports.append("--hidden-import=" + module_name)

pyinstaller_args = [
    os.path.join(".", "pymobiledevice3", "__main__.py"),
    "-y",
    "--hidden-import=ipsw_parser",
    "--hidden-import=zeroconf",
    "--hidden-import=pyimg4",
    "--hidden-import=apple_compress",
    "--hidden-import=zeroconf._utils.ipaddress",
    "--hidden-import=zeroconf._handlers.answers",
    "--hidden-import=readchar",
    "--copy-metadata=pyimg4",
    "--copy-metadata=readchar",
    "--copy-metadata=apple_compress",
    "--add-binary",
    f"{site_packages_path}/pytun_pmd3;pytun_pmd3",
    "--name",
    args.name,
    "--add-data",
    f"{resources_dir}/webinspector:pymobiledevice3/resources/webinspector",
] + (["--onedir"] if args.onedir else ["--onefile"]) + (["--upx-dir", upx_dir] if upx_dir else [])

pyinstaller_args.extend(hidden_imports)
PyInstaller.__main__.run(pyinstaller_args)
