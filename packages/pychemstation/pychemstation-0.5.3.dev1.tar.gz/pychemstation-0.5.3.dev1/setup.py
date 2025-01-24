import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pychemstation",
    version="0.5.3.dev1",
    author="Lucy Hao",
    author_email="lhao03@student.ubc.ca",
    description="Library to interact with Chemstation software, primarily used in Hein lab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/heingroup/pychemstation",
    packages=setuptools.find_packages(),
    install_requires=[
          'polling',
          'seabreeze'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)