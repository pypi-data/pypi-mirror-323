from pathlib import Path

from setuptools import setup, find_packages

long_description =  (Path(__file__).parent / "README.md").read_text()

def get_version() -> str:
    version = {}
    with open(Path(__file__).parent / "aspeechai" / "__version__.py") as f:
        exec(f.read(), version)
    return version["__version__"]


setup(
    name="aspeechai",
    version=get_version(),
    description="ASpeechAI Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ASpeechAI",
    author_email="contact@a-speechai.com",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.19.0",
        "pydantic>=2.9.2",
        "typing-extensions>=3.7",
        "websockets>=11.0",
    ],
    extras_require={
        "extras": ["pyaudio>=0.2.13"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    url="https://github.com/ASpeechAI/aspeechai-python-sdk",
)