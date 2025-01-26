from setuptools import setup, find_packages

setup(
    name='combined_bukmacherska',
    version='0.8.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A package for machine learning and sports analytics',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-repository/combined_bukmacherska',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'scikit-learn',
        'matplotlib',
        'xgboost',
        'catboost',
    ],
)
