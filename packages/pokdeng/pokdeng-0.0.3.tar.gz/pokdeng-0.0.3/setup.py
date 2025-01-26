import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pokdeng",
    version="0.0.3",
    author="Papan Yongmalwong",
    author_email="papillonbee@gmail.com",
    description="pokdeng is a package for simulating rounds of pokdeng games!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/papillonbee/pokdeng",
    packages=setuptools.find_packages(),
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
    ]
)
