from setuptools import setup, find_packages

setup(
    name="tgwindow",
    version="1.1.0",
    description="Библиотека для создания простых окон в Telegram-боте с использованием aiogram.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="PyExecutor",
    author_email="belyankiss@gmail.com",
    url="https://github.com/belyankiss/tgwindow.git",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiogram>=3.0.0"
    ],
    extras_require={
        "dev": ["pytest", "flake8", "black"]
    },
    keywords=["telegram", "aiogram", "bot", "windows", "library"],
    project_urls={
        "Bug Tracker": "https://github.com/belyankiss/tgwindow/issues",
        "Documentation": "https://github.com/belyankiss/tgwindow#readme",
        "Source Code": "https://github.com/belyankiss/tgwindow",
    },
)
