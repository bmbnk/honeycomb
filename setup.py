import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("honeycomb/_version.py") as f:
    version = f.read()

TEST_REQUIRE = ["pytest>=7.0"]

setuptools.setup(
    name="honeycomb",
    version=version,
    author="Jakub Bembenek",
    author_email="jakub.bembenekk@gmail.com",
    description="UHP (Universal Hive Protocol) compliant Hive game engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bmbnk/honeycomb",
    packages=["honeycomb"],
    entry_points={
        "console_scripts": [
            "honeycomb=honeycomb:__main__",
        ]
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=TEST_REQUIRE,
    python_requires=">=3.10",
)
