# Przejdź do głównego katalogu
cd C:\Users\rockd\Desktop\combined_bukmacherska

# Połączenie README1.md i README2.md w README.md w głównym folderze
Get-Content .\combined_bukmacherska1\README1.md, .\combined_bukmacherska2\README2.md |
    Set-Content .\README.md

# Tworzenie pliku LICENSE
Set-Content -Path ".\LICENSE" -Value "MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."

# Tworzenie pliku setup.py z wersją 0.8.0
Set-Content -Path ".\setup.py" -Value "from setuptools import setup, find_packages

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
"
