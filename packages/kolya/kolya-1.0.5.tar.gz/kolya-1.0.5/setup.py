from setuptools import setup, find_packages

setup(
    name="kolya",
    version="1.0.5",
    packages=find_packages(),
    install_requires=[
        # List your project dependencies here, e.g.
        "scipy",
        "numpy",
        "numba",
        "rundec",
    ],
    entry_points={
        "console_scripts": [
            # If your project has command-line scripts, add their entry points here, e.g.
            # "my_script=my_package.my_module:main",
        ],
    },
    python_requires=">=3.6",
    # Add metadata about your project
    author="Matteo Fael, Ilija S. Milutinb, K. Keri Vos",
    author_email="matteo.fael@cern.ch",
    description="A python library for the phenomenology of "
                "B -> X l v inclusive decays.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="GNU GENERAL PUBLIC LICENSE V3.0",
    url="https://gitlab.com/vcb-inclusive/kolya",
    #classifiers=[
    #    "Development Status :: 3 - Alpha",
    #    "License :: OSI Approved :: MIT License",
    #    "Programming Language :: Python :: 3",
    #    "Programming Language :: Python :: 3.6",
    #    "Programming Language :: Python :: 3.7",
    #    "Programming Language :: Python :: 3.8",
    #    "Programming Language :: Python :: 3.9",
    #],
)
