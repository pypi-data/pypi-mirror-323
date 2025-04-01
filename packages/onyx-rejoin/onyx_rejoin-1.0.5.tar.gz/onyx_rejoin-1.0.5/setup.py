from setuptools import setup, find_packages

setup(
    name="onyx-rejoin",
    version="1.0.5",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Add any dependencies here
    ],
    entry_points={
        'console_scripts': [
            'onyx-rejoin-setup=onyx_rejoin.scripts.setup:main',
            'onyx-rejoin-start=onyx_rejoin.scripts.start:main',
        ],
    },
)
