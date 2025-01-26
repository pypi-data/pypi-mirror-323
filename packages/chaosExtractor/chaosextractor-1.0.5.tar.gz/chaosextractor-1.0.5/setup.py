from setuptools import setup, find_packages

setup(
    name='chaosExtractor',
    version='1.0.5',
    packages=find_packages(),
    install_requires=['requests'
    ],
    include_package_data=True,
    description='Multi-package',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='GeekoSaiyan',
    author_email='kreolpony@gmail.com',
    url='https://sites.google.com/view/pasta-apes/c-h-a-o-s',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)