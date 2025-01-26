from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="micropg_lite", 
    version="3.1.1",
    author="TimonW-Dev",
    author_email="timon-github@outlook.com",
    description=(
        "A lightweight PostgreSQL database driver for MicroPython, designed for microcontrollers (e.g., ESP8266) with limited RAM."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimonW-Dev/micropg_lite",
    packages=find_packages(where="."),
    py_modules=["micropg_lite"],
    package_dir={"": "."},
    classifiers=[
        "Programming Language :: Python :: Implementation :: MicroPython",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Other OS",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Database",
    ],
    python_requires=">=3.4",
    keywords="micropython postgresql esp8266 database",
    project_urls={
        "Bug Tracker": "https://github.com/TimonW-Dev/micropg_lite/issues",
        "Documentation": "https://github.com/TimonW-Dev/micropg_lite/wiki",
        "Source Code": "https://github.com/TimonW-Dev/micropg_lite",
    },
)