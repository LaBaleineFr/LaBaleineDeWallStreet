from setuptools import setup, find_packages
import os.path

root = os.path.dirname(__file__)

with open(os.path.join(root, 'requirements.txt'), 'r') as fd:
    requirements = [line.strip() for line in fd if line.strip()]

setup(
    name='baleine',
    version='0.1',
    description='Application code for baleine bot',
    author='Julien Hartmann',
    author_email='juli1.hartmann@gmail.com',
    packages=find_packages(),
    scripts=['main.py'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements
)
