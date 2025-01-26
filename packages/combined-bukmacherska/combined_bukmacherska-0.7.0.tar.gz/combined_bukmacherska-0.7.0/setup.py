from setuptools import setup, find_packages

setup(
    name='combined_bukmacherska',
    version='0.7.0',
    packages=find_packages(),
    install_requires=[
        # Tutaj dodaj zależności, jeśli są jakieś
    ],
    author='Twoje Imię',
    author_email='twoj_email@example.com',
    description='Opis Twojego projektu',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/twoj_github/combined_bukmacherska',  # Zaktualizuj URL
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
