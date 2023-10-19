from distutils.core import setup
from os import path
this_directory = path.abspath(path.dirname(__file__))

setup(
    name="crapsolver_python",
    version="0.0.5",
    packages=["crapsolver_python"],
    url="https://github.com/Implex-ltd/crapsolver-python",
    long_description="solve crap using crapsolver !",
    long_description_content_type="text/markdown",
    license="APACHE",
    author="0xF7A4C6",
    description="crapsolver library for Python",
    requires=["requests"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    use_scm_version=True,
    setup_requires=["setuptools_scm", "wheel"],
    install_requires=["httpx"],
    python_requires=">=3",
    project_urls={
        "Documentation": 'https://crapsolver.gitbook.io',
        "Source": 'https://github.com/Implex-ltd/crapsolver-python',
        "Tracker": 'https://github.com/Implex-ltd/crapsolver-python/issues',
    },
)
