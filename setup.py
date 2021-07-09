from setuptools import setup, find_packages

setup(
    name='restless',
    version='0.0.1',
    description='A router for AWS Lambda, Flask and Azure Functions',
    packages=find_packages(),
    install_requires=['jsonschema', 'pydantic'],
    package_data={
        '': [
            './flask/swagger/*',
        ]
    },
    extras_require={
        'azure': ['azure-functions'],
        'tests': ['requests']
    }
)
