from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nursing-ai-sdk",
    version="1.0.0",
    author="Nursing Training AI",
    author_email="developers@nursingtrainingai.com",
    description="Official Python SDK for Nursing Training AI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ginx172/Nursing-Training-AI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "dataclasses>=0.6; python_version<'3.7'"
    ],
    extras_require={
        "dev": ["pytest>=7.0", "black>=23.0", "mypy>=1.0"],
    },
    keywords="nursing healthcare training ai nhs enterprise api sdk",
    project_urls={
        "Documentation": "https://docs.nursingtrainingai.com",
        "Source": "https://github.com/Ginx172/Nursing-Training-AI",
        "Bug Reports": "https://github.com/Ginx172/Nursing-Training-AI/issues",
    }
)

