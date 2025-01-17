from setuptools import find_packages, setup

from dandy.const import VERSION

with open('LICENSE.md', encoding="utf-8") as license_handle:
    license_file = license_handle.read()

setup(
    name="dandy",
    version=VERSION,
    description="Intelligence Bot Framework",
    long_description="Dandy is a framework for developing programmatic intelligent bots and workflows. It's opinionated, usefully magical, and designed to be incredibly pythonic.",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["dandy", "ai", "llm", "agent", "prompt", "gpt", "bot", "workflow", "automation", "artificial intelligence"],
    author="Nathan Johnson",
    author_email="info@stratusadv.com",
    url="https://github.com/stratusadv/dandy",
    license=license_file,
    packages=find_packages(exclude=["docs"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.8.2",
    ],
    entry_points = {
        "console_scripts": [
            "dandy = dandy.cli.main:main",
        ]
    }
)