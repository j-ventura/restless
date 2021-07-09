from setuptools import setup, find_packages

extras = {
    'azure': ['azure-functions'],
    'tests': ['requests'],
    'spec': ['pyyaml']
}

all_deps = set()

for deps in extras.values():
    for dep in deps:
        all_deps.add(dep)

setup(
    name='restless-cloud',
    version='0.0.1',
    author="Joaquim Ventura",
    author_email="allaphor@gmail.com",
    description='A router for AWS Lambda and Azure Functions',
    packages=find_packages(),
    install_requires=['jsonschema', 'pydantic'],
    extras_require=dict(
        all=list(all_deps),
        **extras
    )
)
