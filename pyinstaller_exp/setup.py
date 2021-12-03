from setuptools import setup, find_packages


setup(
    name="pyinstaller_test",
    version="0.0.1",
    author="simple",
    description="Quickly build a configurable service.",
    packages=find_packages(exclude=("config")),
    python_requires=">=3.6",
    install_requires=[
        "Flask>=1.1.2",
        "Flask-RESTful>=0.3.8",
        "fvcore",
        "Pillow",
        "service-streamer>=0.1.2",
        "termcolor>=1.1",
        "tqdm>=4.46.1",
        "yacs>=0.1.7",
        "requests>=2.24",
        "tabulate",
    ],
)

