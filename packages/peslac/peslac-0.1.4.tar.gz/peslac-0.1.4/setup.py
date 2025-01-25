from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="peslac",
    version="0.1.4",
    keywords=[
        "peslac",
        "api",
        "documents",
        "tools",
        "nodejs",
        "rag",
        "ai",
        "llm",
        "remote-file",
        "remote-file-processing",
        "document-processing",
        "file-processing",
        "ocr",
        "image-processing",
        "pdf-processing",
        "document-ocr",
        "image-ocr",
        "pdf-ocr",
        "pdf-splitter",
        "pdf-merger"
    ],
    packages=find_packages(),
    install_requires=[
        "requests",
        "requests-toolbelt",
    ],
    description="A Python package for the Peslac API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jibril Kala",
    author_email="support@peslac.com",
    url="https://github.com/peslacai/peslac-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ],
    python_requires=">=3.7",
    project_urls={
        "Bug Tracker": "https://github.com/peslacai/peslac-python/issues",
        "Source Code": "https://github.com/peslacai/peslac-python",
        "Documentation": "https://github.com/peslacai/peslac-python#readme",
    },
)
