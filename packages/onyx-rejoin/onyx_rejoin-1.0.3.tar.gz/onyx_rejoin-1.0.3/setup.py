from setuptools import setup, find_packages

setup(
    name="onyx-rejoin",
    version="1.0.3",  # Increment version number
    packages=find_packages(),
    install_requires=[
        # Add any dependencies here if needed
    ],
    entry_points={
        'console_scripts': [
            'onyx rejoin = onyx.__init__:main',  # Entry point for the command
        ],
    },
)
