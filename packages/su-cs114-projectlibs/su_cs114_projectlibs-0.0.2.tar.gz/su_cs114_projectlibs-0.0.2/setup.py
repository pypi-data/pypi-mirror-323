from setuptools import find_packages, setup
from distutils.core import setup
from setuptools.command.install import install
from os import chmod

stdlib_modules=['qrcodelib']

with open("README.md", "r") as fh:
    long_description = fh.read()

class MyInstall(install):
    def run(self):
        # Perform a normal install.
        install.run(self)
        # Change permissions of the installed .py and .pyc files.
        print(self.get_outputs())
        for fileName in self.get_outputs():
            if fileName.endswith(('.py', '.pyc')):
                for stdlib_module in stdlib_modules:
                    if stdlib_module in fileName:
                        chmod(fileName, 420)  # 420 decimal = 644 octal
                        break

setup(
    name="su-cs114-projectlibs",
    version="0.0.2",
    description='Stellenbosch University Python 3 code for 2025 CS114 semester project.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Marcel Dunaiski",
    author_email='marceldunaiski@sun.ac.za',
    #url="...",
    license="GNU General Public License v3 (GPLv3)",
    python_requires='>=3.8',
    packages=find_packages(exclude=["examples", "tests"]),
    include_package_data=True,
    install_requires=[
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "coveralls",
        ],
    },
    py_modules=stdlib_modules,
    package_dir={'': 'su/cs1/'},
    cmdclass={'install': MyInstall},
    zip_safe=False,
    platforms="any",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
