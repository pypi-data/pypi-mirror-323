from setuptools import setup, find_packages

setup(
    name="molidb",
    version="0.1.7",
    packages=find_packages(),
    install_requires=[
        'requests',
        'pycryptodome',
        'python-dotenv',
    ],
    author="fluffy-melli",
    author_email="yummyshibadog@gmail.com",
    description="A package for managing collections with AES encryption and compression",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fluffy-melli/MoliDB-pypi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="MIT",
)
