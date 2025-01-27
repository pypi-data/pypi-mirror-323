from setuptools import setup, find_packages

setup(
    name='zimbabwean_id_number_validator',
    version='1.0.2',
    author='Wellington Mpofu',
    author_email='wellington.t.mpofu@gmail.com',
    description='Zimbabwean ID Number Validator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
