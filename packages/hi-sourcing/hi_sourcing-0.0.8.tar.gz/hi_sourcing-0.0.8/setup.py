from setuptools import setup, find_packages

setup(
    name="hi-sourcing",
    version="0.0.8",
    author="J L",
    author_email="jliu5277@gmail.com",
    description="A similarity search utility for data sourcing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/xileven/hi-sourcing",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas",
        "numpy",
        "faiss-cpu",
    ],
    package_data={
        '': ['README.md'],
    },
    project_urls={
        'Documentation': 'https://github.com/xileven/hi-sourcing',
        'Source': 'https://github.com/xileven/hi-sourcing',
        'Tracker': 'https://github.com/xileven/hi-sourcing/issues',
    },
)
