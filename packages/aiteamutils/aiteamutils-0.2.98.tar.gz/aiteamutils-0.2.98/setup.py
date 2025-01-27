from setuptools import setup, find_packages

setup(
    name="aiteamutils",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "python-jose",
    ],
    author="AI Team",
    description="AI Team Utilities",
    python_requires=">=3.8",
) 