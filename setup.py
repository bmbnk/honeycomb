import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("honeycomb/_version.py") as f:
    version_line = f.readline()
    globals_values = {}
    exec(version_line, globals_values)
    version = globals_values["__version__"]

with open("requirements-dev.txt") as f:
    test_requires = [
        line for line in f.read().splitlines() if line and not line.startswith("#")
    ]

setuptools.setup(
    name="honeycomb",
    version=version,
    author="Jakub Bembenek",
    author_email="jakub.bembenekk@gmail.com",
    description="UHP (Universal Hive Protocol) compliant Hive game engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bmbnk/honeycomb",
    packages=setuptools.find_packages(exclude=["tests"]),
    entry_points={
        "console_scripts": [
            "honeycomb=honeycomb.__main__:main",
        ]
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=test_requires,
    python_requires=">=3.10",
)
