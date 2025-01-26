from setuptools import setup

setup(
    name='scp_api_client',
    version='0.3.0',
    description='A Python package for Supply Chain Proof client functionality',
    url='https://github.com/AndresNamm/scp_api_client',
    author='Andres Namm',
    author_email='andres.namm.001@gmail.com',
    license='BSD 2-clause',
    packages=['scp_api_client'],
    install_requires=[ 'numpy','requests'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
