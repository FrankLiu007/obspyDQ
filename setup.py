import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="obspyDQ", # Replace with your own username
    version="0.1",
    author="Liu qimin",
    author_email="liuqimin2009@163.com",
    description="Seismic Data query Frame with obspy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FrankLiu007/obspyDQ",
    project_urls={
        "Bug Tracker": "https://github.com/FrankLiu007/obspyDQ/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    #package_dir={"": "src"},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
