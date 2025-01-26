from setuptools import setup, find_packages

VERSION = '1.1' 
DESCRIPTION = 'Open GnuCash XML book'
LONG_DESCRIPTION = 'Open GnuCash XML book and provide account information to Python'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="gnucashxml", 
        version=VERSION,
        author="David A Nagy",
        author_email="dalexnagy@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'

        keywords=['python', 'gnucashxml'],
        classifiers= [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: End Users/Desktop",
            "Programming Language :: Python :: 3",
        ]
)
