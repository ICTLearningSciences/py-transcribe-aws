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


def _read_version():
    with open('VERSION') as version_file:
        return version_file.read().strip()


setup(
    name="py_transcribe_aws",
    version=_read_version(),
    author_email="larrykirschner@gmail.com",
    description="framework for synchronous batch speech-to-text transcription using backends like AWS, Watson, etc.",
    packages=packages,
    package_dir={'transcribe_aws': 'transcribe_aws'},
    package_data={
        "transcribe_aws": ["py.typed"],
    },
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
