from setuptools import setup, find_packages

setup(
    name="clonearmy",
    version="0.2.4",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
) 