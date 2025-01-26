from setuptools import setup, find_packages

setup(
    name="superline",
    version="0.1",
    packages=find_packages(),
    requires=[
        "base64",
        "os",
        "subprocess",
        "sys",
        "json",
        "pyaes",  # Assurez-vous que ce module est installé via pip
        "random",
        "shutil",
        "sqlite3",
        "re",
        "traceback",
        "time",
        "ctypes",
        "logging",
        "zlib",
        "urllib3"
    ]
)