from setuptools import setup, find_packages

setup(
    name="MySqlWebApp",
    version="1.1",
    author="Abu Awaish",
    author_email="abuawaish7@gmail.com",
    description="A Python package for building dynamic MySQL-powered web applications with template support",
    long_description=open('README.rst').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type="text/x-rst",  # Use Markdown for README
    url="https://github.com/abuawaish/Crud_app",
    packages=find_packages(),
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
    package_data={
        "MySqlWebApp": ["templates/*"],  # Include all files in the templates folder
    },
    install_requires=['Flask','Flask-MySQLdb'],
    license="MIT",
    keywords="Web App",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Specify the minimum Python version
)
