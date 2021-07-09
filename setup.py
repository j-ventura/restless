from setuptools import setup, find_packages

extras = {
    'azure': ['azure-functions'],
    'tests': ['requests']
}

all_deps = set()

for deps in extras.values():
    for dep in deps:
        all_deps.add(dep)

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
    extras_require=dict(
        all=list(all_deps),
        **extras
    )
)
