from setuptools import setup, find_packages

setup(
    name='inovyo_api',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Modulo-Inovyo-API',
    author_email='admin@inovyo.com',
    description='Biblioteca para integração com as APIs da Inovyo',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
)
