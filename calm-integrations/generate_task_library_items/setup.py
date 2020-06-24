from setuptools import setup, find_packages

with open('README.md', encoding='UTF-8') as f:
    readme = f.read()

setup(
    name='generate_task_library_items',
    version='1.0',
    description='Create task library items from a collection of local scripts',
    long_description=readme,
    author='Nutanix',
    install_requires=[
        'requests'
    ],
    packages=find_packages('.'),
    package_dir={'': '.'}
)