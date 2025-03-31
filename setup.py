from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the contents of the requirements file
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="kaizenroi",
    version="2.0.0",
    author="KaizenROI Analytics",
    author_email="support@kaizenroi.com",
    description="Smart Return Optimization Suite for e-commerce and retail businesses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kaizenroi",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "kaizenroi": ["assets/*"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kaizenroi=kaizenroi.app:main",
        ],
    },
)
