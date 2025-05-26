from setuptools import setup, find_packages

setup(
    name="smart-todo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "inquirer>=2.7.0",
        "python-dateutil>=2.8.0",
        "google-genai>=1.0.0"
    ],
    entry_points={
        'console_scripts': [
            'todo=smart_todo.cli:cli',
        ],
    },
    author="Smart Todo Team",
    author_email="smart.todo@example.com",
    description="A smart TODO list CLI that suggests tasks based on time and mood",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    keywords="todo, task-management, cli, productivity",
    url="https://github.com/yourusername/smart-todo",
)
