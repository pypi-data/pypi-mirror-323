from setuptools import setup, find_packages

setup(
    name='somali_spelling_correction',
    version='0.6',  # Update the version if needed
    packages=find_packages(),
    include_package_data=True,  # Ensures package data is included
    package_data={'somali_spelling_correction': ['Dataset_Spelling.csv']},  # Include the dataset
    description='Somali Spelling Correction Package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='R&D',
    author_email='abdoldevtra@example.com',
    url='https://github.com/abdoltd/somali_spelling_correction',
    # license='MIT',
    # classifiers=[
    #     'Programming Language :: Python :: 3',
    #     'License :: OSI Approved :: MIT License',
    #     'Operating System :: OS Independent',
    # ],
    # python_requires='>=3.6',
)
