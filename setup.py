from setuptools import find_packages, setup

from dandy import __version__

setup(
    name="dandy",
    version=__version__,
    description="An Agentic AI Framework",
    long_description=open("README.md").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["dandy", "ai", "llm", "agent", "prompt", "gpt"],
    author="Nathan Johnson",
    author_email="info@stratusadv.com",
    url="https://github.com/stratusadv/dandy",
    license="MIT",
    packages=find_packages(exclude=["docs"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[],
)