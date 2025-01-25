from setuptools import setup, find_packages

setup(
    name="udfc",
    version="0.3",
    packages=find_packages(),
    install_requires=[], 
    entry_points={
        "console_scripts": [
            "udfc=udfc.main:main",  
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    author='juanvel400',             
    author_email='juanvel400@proton.me',
    description='A Small tool to create .desktop files',
    long_description=open('README.md', encoding='utf-8').read(),

    long_description_content_type='text/markdown',
    url='https://github.com/juanvel4000/udfc', 

)
