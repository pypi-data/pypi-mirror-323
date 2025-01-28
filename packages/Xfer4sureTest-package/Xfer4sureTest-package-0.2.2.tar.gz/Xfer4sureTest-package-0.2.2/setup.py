from setuptools import setup, find_packages

setup(
    name="Xfer4sureTest-package",
    version="0.2.2",
    packages=find_packages(),
    package_data={
        'Xfer4sureTest_package': ['__pycache__/*.pyc'],  # Include the .pyc files in the package
    },
    install_requires=[],
    entry_points={
        'console_scripts': [
            'run-your-script = Xfer4sureTest_package.script:run',  # Add this to run `run` from script.pyc
        ],
    },
)

