from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='tcmaker',
    version='0.0.5',
    description='testcase maker for online judge',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='csvega',
    author_email='vega4792@gmail.com',
    url='https://github.com/csvega/tcmaker',
    install_requires=[],
    packages=find_packages(exclude=[]),
    keywords=['testcase', 'online judge', 'OJ', 'hustoj'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
)
