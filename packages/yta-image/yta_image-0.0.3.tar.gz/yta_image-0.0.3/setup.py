from setuptools import setup, find_packages


VERSION = '0.0.3'
DESCRIPTION = 'Youtube Image Module.'
LONG_DESCRIPTION = 'This is the Youtube Autonomous Image module'

setup(
        name = "yta_image", 
        version = VERSION,
        author = "Daniel Alcalá",
        author_email = "<danielalcalavalera@gmail.com>",
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        packages = find_packages(),
        install_requires = [
            'yta_general_utils',
            'pillow',
            'numpy'
        ],
        
        keywords = [
            'youtube autonomous image module software'
        ],
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)