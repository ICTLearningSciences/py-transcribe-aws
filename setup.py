from setuptools import setup, find_packages
from os import path


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def _read_dependencies():
    requirements_file = "requirements.txt"
    with open(requirements_file) as fin:
        return [line.strip() for line in fin if line]


packages = find_packages()
requirements = _read_dependencies()

setup(
    name="transcribe",
    version="1.0.0",
    author_email="larrykirschner@gmail.com",
    description="framework for synchronous batch speech-to-text transcription using backends like AWS, Watson, etc.",
    packages=packages,
    package_dir={'transcribe': 'transcribe'},
    package_data={
        "transcribe": ["py.typed"],
    },
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
