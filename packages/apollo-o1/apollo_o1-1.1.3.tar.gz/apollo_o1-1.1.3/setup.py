from setuptools import setup, find_packages

setup(
    name="apollo-o1",
    version="1.1.3",
    description="An AI-powered Command-Line Interface designed to streamline the SDLC by automating project workflows, including source control, CI/CD, ticket and documentation generation, and other processes.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Stratum Labs",
    author_email="hq@stratumlabs.ai",
    url="https://github.com/dj-io/apollo",
    project_urls={
        "Code": "https://github.com/dj-io/apollo-o1",
        "Documentation": "https://github.com/dj-io/apollo-o1/blob/main/README.md",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "questionary",
        "click",
        "python-dotenv",
        "halo",
        "flake8",
        "black",
    ],
    extras_require={
        "dev": ["pytest"],
    },
    entry_points={
        "console_scripts": [
            "apollo=apollo.main:apollo",  # Maps the `apollo` command to the `apollo()` group function
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
)
