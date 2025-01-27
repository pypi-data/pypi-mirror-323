from setuptools import setup, find_packages

setup(
    name="mathguess",  # Your program's name
    version="1.2",  # The version of your package
    description="generates random multiplication numbers",
    author="Adrian",
    author_email="openbioscience@gmail.com",
    url="https://github.com/yourusername/my_program",  # Optional, link to project homepage
    packages=find_packages(),  # Automatically find and include all packages
    install_requires=[  # List any dependencies here
        # 'requests', 'numpy', etc.
    ],
    classifiers=[  # Optional, specify relevant classifiers
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={  # Optional, for defining CLI commands
        'console_scripts': [
            'mathguess = mathguess.main:main',  # This line specifies the command-line script
        ],
    },
)

