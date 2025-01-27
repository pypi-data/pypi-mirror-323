from setuptools import setup, find_packages

setup(
    name="mcp-hive-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "jinja2>=3.0.0",
        "rich>=10.0.0",
        "python-dotenv>=0.19.0",
        "langchain-core>=0.1.0",
        "langchain-anthropic>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-hive=cli:main",
        ],
    },
    package_data={
        "cli": ["templates/agent/*"],
    },
    author="Ashish Mandal",
    author_email="mandal.ashish@codenation.co.in",
    description="CLI tool for creating MCP agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/trilogy-group/mcp-hive-app",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
