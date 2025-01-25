from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='embdiv',
    version='0.0.1',
    author='1kkiren',
    author_email='1kkiren@mail.ru',
    description='Library for dividing the Embedding layer of the LLM.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/1kkiRen/Embeddings-Division',
    packages=find_packages(),
    install_requires=[
        'cachetools==5.5.0',
        'torch==2.5.1+cu124',
        'transformers==4.45.2',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    keywords='embeddings division nlp',
    project_urls={
        'GitHub': 'https://github.com/1kkiRen/Embeddings-Division'
    },
    python_requires='>=3.9'
)
