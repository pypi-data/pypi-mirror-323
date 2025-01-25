from setuptools import setup, find_packages

setup(
    name="teachers",  # Replace with your app name
    version="5.1.4",       # Replace with your version
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.0",
        "mysqlclient",  # Adjust dependencies as per your project
    ],
    classifiers=[
        "Framework :: Django",
        'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.5',
        "License :: OSI Approved :: MIT License",
    ],
)