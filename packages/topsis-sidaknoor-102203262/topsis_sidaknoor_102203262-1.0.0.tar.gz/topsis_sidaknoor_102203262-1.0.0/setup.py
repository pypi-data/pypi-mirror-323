import pathlib
from importlib_metadata import entry_points
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE /"README.md").read_text()

setup(
    name = 'topsis-sidaknoor-102203262',           
    version = '1.0.0',    
    packages=['topsis'] ,
    long_description=README,
    long_description_content_type='text/markdown',
    license='MIT',        
    description = 'A TOPSIS implemented function that returns rank of rows',   
    author = 'Sidak Noor Singh',                   
    author_email = 'ssingh9_be22@thapr.edu',      
    url = 'https://test.pypi.org/project/topsis-sidaknoor-102203262/',   
    download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    
    install_requires=[            
          'numpy',
          'pandas',
      ],
    classifiers=[
        'Development Status :: 3 - Alpha',      
        'Intended Audience :: Developers',      
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',      
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
      entry_points= {
        "console_scripts": [
          "topsis=topsis.__main__:main",
      ]}
)