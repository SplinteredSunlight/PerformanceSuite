from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="performance_suite",
    version="0.1.0",
    author="SplinteredSunlight",
    author_email="example@example.com",
    description="A comprehensive system for live musical performances with AI-driven virtual bandmates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SplinteredSunlight/PerformanceSuite",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Musicians",
        "Topic :: Multimedia :: Sound/Audio",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
        ],
    },
)
