from setuptools import setup
long="""Use C++ style stream to read and write data in Python
It supports:
- C++ style iostream
- C++ style stringstream
- C++ style fstream
- C++ style but only in this library:
    bytesstream
    voicestream (use voicestream_init(pyttsxn.init()) to initialize (n ∈ {blank, 2, 3, 4}))
    only on Windows: keystream (use keystream_init() to initialize, use keybd >> var to read key and keybd << bytes to write chars)

Special thanks to:
- pyttsx4
"""
setup(
    name='pycppstreams',
    version='0.0.2',
    packages=["pycppstreams"],
    install_requires=["pyttsx4"],
    requires=["pyttsx4"],
    author='dianbtcmputr',
    author_email='3663144423@qq.com',
    url="https://pypi.org",
    description='A C++ style stream library for Python',
    long_description=long,
    long_description_content_type='text/plain',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)