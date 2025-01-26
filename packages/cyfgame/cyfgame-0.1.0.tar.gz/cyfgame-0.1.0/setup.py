from setuptools import setup, find_packages

setup(
    name='cyfgame',
    version='0.1.0',
    description='Give you a better programming experience to play games.',
    author='cyf',
    author_email='chengyf1314@qq.com',
    packages=find_packages(),
    install_requires=['pygame'],
    tests_require=['unittest'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)