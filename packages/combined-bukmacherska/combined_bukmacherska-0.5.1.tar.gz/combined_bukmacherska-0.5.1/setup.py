from setuptools import setup, find_packages

setup(
    name="combined_bukmacherska",
    version="0.5.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "scikit-learn",
        "xgboost",
        "catboost",
    ],
    author="Twoje Imię",
    author_email="your.email@example.com",
    description="Tools for analyzing sports statistics and using machine learning to assist in betting strategies.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo-url",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
