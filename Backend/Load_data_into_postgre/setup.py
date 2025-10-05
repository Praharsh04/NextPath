from setuptools import setup, find_packages

setup(
    name='psychometry-data-importer',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'import-psychometry-data=insert_values:main',
        ],
    },
    install_requires=[
        'pandas',
        'psycopg2-binary',
        'python-dotenv',
    ],
)
