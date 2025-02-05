from setuptools import setup, find_packages

setup(
    name="codebase-markdown-visualizer",
    version="0.1.0",
    description="Transform a Python codebase into interlinked markdown files for Obsidian.",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyYAML>=6.0",
        "flake8>=3.9",
    ],
    entry_points={
        "console_scripts": [
            "codebase-visualizer=main:main",
        ],
    },
)
