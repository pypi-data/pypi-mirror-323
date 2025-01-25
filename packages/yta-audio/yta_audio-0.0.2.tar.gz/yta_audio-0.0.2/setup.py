from setuptools import setup, find_packages


VERSION = '0.0.2'
DESCRIPTION = 'Youtube Autonomous Audio Module.'
LONG_DESCRIPTION = 'This is the Youtube Autonomous Audio module'

setup(
        name = "yta_audio", 
        version = VERSION,
        author = "Daniel Alcalá",
        author_email = "<danielalcalavalera@gmail.com>",
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        packages = find_packages(),
        install_requires = [
            'yta_general_utils',
            'pydub',
            'moviepy'
        ],
        
        keywords = [
            'youtube autonomous audio module software'
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