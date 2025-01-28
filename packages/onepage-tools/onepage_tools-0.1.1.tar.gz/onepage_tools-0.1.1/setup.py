from setuptools import setup, find_packages,Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="onepage_tools._internal.api_logic",  # Name of the compiled module
        sources=["onepage_tools/_internal/api_logic.pyx"],  # Source file in Python (converted to .pyx)
    ),
]

setup(
    name="onepage_tools",
    version="0.1.1",
    packages=find_packages(),
    install_requires=["requests","typing"],
    python_requires=">=3.11",
        classifiers=[
        "Programming Language :: Python :: 3",
    ],
     ext_modules=cythonize(
         extensions,
         compiler_directives={'language_level': '3'} 
         ),
)
