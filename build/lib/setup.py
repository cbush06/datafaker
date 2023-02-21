from setuptools import find_packages, setup

setup(
    name = 'datafaker',
    version = '1.0.0',
    description = 'Populates the MIGYM database with fake data',
    package_dir={'':'.'},
    install_requires = [
        "click>=8.1.3",
        "Faker>=15.1.3",
        "psycopg2-binary>=2.9.5",
        "python-dateutil>=2.8.2",
        "python-stopwatch>=1.0.5",
        "PyYAML>=6.0",
        "six>=1.16.0",
        "SQLAlchemy>=1.4.41",
        "termcolor>=2.1.0",
        "typing_extensions>=4.4.0"
    ],
    entry_points = {
        'console_scripts': ['datafaker=main:load']
    }
)