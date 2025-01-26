#!/usr/bin/env python3

import sys
import os

from setuptools import find_packages, setup
from setuptools_rust import RustExtension

PACKAGE_NAME = "tgcrypto-optimized"
PACKAGE_VERSION = "0.3.4"
ENVVAR_VERSION_SUFFIX = "PYPI_SETUP_VERSION_SUFFIX"


def main(args):

    setup(
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION+os.environ.get(ENVVAR_VERSION_SUFFIX, ""),
        description="Cryptographic utilities for Telegram.",
        long_description_content_type="text/x-rst",

        author="Telectron inc.",

        license="CC0",

        # https://pypi.python.org/pypi?:action=list_classifiers
        classifiers=[
            "Development Status :: 4 - Beta",

            "Intended Audience :: Developers",
            "Topic :: Security :: Cryptography",

            "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",

            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
        ],
        keywords="telegram crypto cryptography mtproto aes",

        packages=find_packages(),
        python_requires=">=3.3",
        rust_extensions=[RustExtension("tgcrypto_optimized.tgcrypto_optimized")],
        zip_safe=False
    )


if __name__ == '__main__':
    main(sys.argv)
