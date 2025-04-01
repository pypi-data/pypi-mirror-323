from setuptools import setup, find_packages

setup(
    name='helpful-pys',  # Replace with your package name
    version='0.2.1',  # Updated version
    author='Lawrence Chin',  # Replace with your name
    author_email='lawrence.chin@gusto.com',  # Replace with your email
    description='A helper package to use common functions',  # A brief description
    long_description=open('README.md').read(),  # Read the README file for a longer description
    long_description_content_type='text/markdown',  # Specify the format of the long description
    url='https://github.com/Gusto/helpful-pys',  # Replace with your repository URL
    packages=find_packages(),  # Automatically find packages in your_package/
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',  # Specify the minimum Python version required
    install_requires=[
        'redshift_connector>=2.1.3',
        'pandas>=2.2.3',
        'gspread>=6.1.3',
    ],
    license='MIT',  # Specify the license type here
)
