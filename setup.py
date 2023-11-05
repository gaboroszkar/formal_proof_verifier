from setuptools import setup, find_packages

setup(
    name="formal_proof_verifier",
    version="0.1",
    packages=find_packages(),
    python_requires=">=3.11",
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ]
    },
)
