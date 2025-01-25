from setuptools import setup, find_packages

setup(
    name="somali_spelling_correction",
    version="0.1.0",
    author="R&D",
    author_email="abdoldevtra@example.com",
    description="A Somali spelling correction library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/abdoltd/somali_spelling_correction",
    packages=find_packages(),
    # include_package_data=True,
    # python_requires=">=3.6",
    # install_requires=[],
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ],
)
