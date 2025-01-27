from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))


# def parse_requirements(filename):
#     """Parse the requirements.txt file."""
#     with open(filename, 'r') as f:
#         return [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]


with open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

# Read dependencies from requirements.txt
# requirements = parse_requirements('requirements.txt')

setup(
    name="bangla-ipa",
    version="1.0",
    author="Biplab Kumar Sarkar, Afrar Jahin, Asif Shusmit",
    author_email="bip.sec22@gmail.com",
    description="A Python module for generating Bangla IPA transliterations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bipsec/bangla-ipa",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "certifi==2024.12.14",
        "charset-normalizer==3.4.1",
        "colorama==0.4.6",
        "docutils==0.21.2",
        "filelock==3.17.0",
        "fsspec==2024.12.0",
        "id==1.5.0",
        "idna==3.10",
        "jaraco.classes==3.4.0",
        "jaraco.context==6.0.1",
        "jaraco.functools==4.1.0",
        "Jinja2==3.1.5",
        "keyring==25.6.0",
        "markdown-it-py==3.0.0",
        "MarkupSafe==3.0.2",
        "mdurl==0.1.2",
        "more-itertools==10.6.0",
        "mpmath==1.3.0",
        "networkx==3.4.2",
        "nh3==0.2.20",
        "numpy==2.2.2",
        "packaging==24.2",
        "pandas==2.2.3",
        "Pygments==2.19.1",
        "python-dateutil==2.9.0.post0",
        "pytz==2024.2",
        "pywin32-ctypes==0.2.3",
        "readme_renderer==44.0",
        "requests==2.32.3",
        "requests-toolbelt==1.0.0",
        "rfc3986==2.0.0",
        "rich==13.9.4",
        "sentencepiece==0.2.0",
        "setuptools==75.8.0",
        "six==1.17.0",
        "sympy==1.13.3",
        "torch==2.4.1",
        "torchdata==0.7.1",
        "torchtext==0.6.0",
        "tqdm==4.67.1",
        "twine==6.1.0",
        "typing_extensions==4.12.2",
        "tzdata==2025.1",
        "urllib3==2.3.0",
        "wheel==0.45.1",

    ],
    include_package_data=True,
    package_data={
        'bangla_ipa': [
            'data/*.csv',
            'model/*.pth',
        ],
    },
    keywords=[
        "python", "IPA", "Bangla IPA", "International Phonetic Alphabet",
        "Bangla linguistics", "transliteration"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
