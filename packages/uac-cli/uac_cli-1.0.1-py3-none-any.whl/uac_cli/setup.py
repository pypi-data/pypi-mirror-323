from setuptools import find_packages, setup

from uac_cli import __version__

version = __version__


def main():
    with open("README.md", "r") as readme:
        long_description = readme.read()
    setup(
        name="uac-cli",
        version=version,
        author_email="support@stonebranch.com",
        license="CC BY-NC 4.0",
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            "uac-api >= 0.4.5",
            "setuptools >= 44.1.1",
            "click == 8.1.6",
            "jsonpath-ng == 1.5.3",
            "PyYAML",
        ],
        author="Stonebranch Extensions Team",
        description="A CLI tool for executing commands against the Stonebranch UAC API",
        entry_points={"console_scripts": ["uac=uac_cli.main:run"]},
        python_requires=">=3.7",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        long_description=long_description,
        long_description_content_type="text/markdown",
    )


if __name__ == "__main__":
    main()
