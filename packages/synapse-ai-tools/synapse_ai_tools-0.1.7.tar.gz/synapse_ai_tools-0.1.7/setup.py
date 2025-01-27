from setuptools import setup, find_packages

setup(
    name="synapse_ai_tools",  
    version="0.1.7",  
    description="A Python package for artificial intelligence development, providing utilities for machine learning, deep learning, data processing, and model deployment.",  
    long_description=open('README.md').read(),  
    long_description_content_type="text/markdown",  
    author="SYNAPSE AI SAS",  
    author_email="servicios@groupsynapseai.com",  
    # url="",  
    packages=find_packages(),  
    install_requires=[  
        "matplotlib",  
        "seaborn",     
        "pandas",      
    ],
    classifiers=[  
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  
)