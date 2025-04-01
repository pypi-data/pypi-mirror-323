from setuptools import setup, find_packages

setup(
    name="onyx-roblox-rejoin",
    version="1.0.7",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Add any dependencies here
    ],
    entry_points={
        'console_scripts': [
            'onyx rejoin setup=onyx_roblox_rejoin.scripts.setup:main',
            'onyx rejoin start=onyx_roblox_rejoin.scripts.start:main',
        ],
    },
)
