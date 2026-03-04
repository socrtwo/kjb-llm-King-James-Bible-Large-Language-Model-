from setuptools import setup, find_packages

setup(
    name="kjb-llm",
    version="0.1.0",
    description="King James Bible Large Language Model -- RAG-based Q&A grounded in the KJB",
    author="socrtwo",
    url="https://github.com/socrtwo/kjb-llm-King-James-Bible-Large-Language-Model-",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.0.0",
        "chromadb>=0.4.0",
        "requests>=2.31.0",
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0"],
    },
    entry_points={
        "console_scripts": [
            "kjb-query=kjb_llm.query:main",
            "kjb-ingest=kjb_llm.ingest:main",
            "kjb-server=kjb_llm.api:main",
        ],
    },
)
