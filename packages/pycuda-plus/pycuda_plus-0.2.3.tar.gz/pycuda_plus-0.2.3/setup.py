from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pycuda_plus',
    version='0.2.3',
    description='User-friendly library to enhance PyCUDA functionality',
    long_description=long_description,
    long_description_content_type="text/markdown",  # Specifies the format of the long description
    author='Phillip Chananda',
    author_email='takuphilchan@gmail.com',
    url='https://github.com/takuphilchan/pycuda_plus',
    packages=find_packages(),
    install_requires = [
    'pycuda',
    'numpy',
    'six',
    'matplotlib',
    'seaborn',
    'pandas',
    # other dependencies
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    project_urls={
        "Bug Tracker": "https://github.com/takuphilchan/pycuda_plus/issues",
        "Documentation": "https://github.com/takuphilchan/pycuda_plus#readme",
        "Source Code": "https://github.com/takuphilchan/pycuda_plus",
    },
)
