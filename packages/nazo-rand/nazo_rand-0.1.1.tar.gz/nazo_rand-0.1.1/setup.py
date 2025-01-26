from setuptools import setup, Extension
from Cython.Build import cythonize
from sys import platform


def readme():
    with open("README.md") as f:
        return f.read()


extra_compile_args = []
extra_link_args = []

if platform == "win32":
    extra_compile_args = ["/std:c++17", "/O2"]
elif platform == "linux":
    extra_compile_args = ["-std=c++17", "-O3"]
    extra_link_args = ["-Wl,-O3"]
elif platform == "darwin":  # macOS
    extra_compile_args = ["-std=c++17", "-O3"]
    extra_link_args = ["-Wl,-dead_strip"]

setup(
    name="nazo_rand",
    ext_modules=cythonize(
        Extension(
            name="",
            sources=["nazo_rand/nazo_rand.pyx"],
            language=["c++"],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        ),
        compiler_directives={
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
            "binding": True,
            "cdivision": True,
        },
    ),
    author="bymoye",
    author_email="s3moye@gmail.com",
    version="0.1.1",
    description="A fast random number generator for python",
    long_description=readme(),
    long_description_content_type="text/markdown",
    license="Free for non-commercial use",
    package_data={
        "": [
            "nazo_rand/nazo_rand.pyi",
            "nazo_rand/nazo_rand.pyx",
            "nazo_rand/nazo_rand.hpp",
            "nazo_rand/nazo_rand.pxd",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Cython",
        "Programming Language :: C++",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    packages=["nazo_rand"],
)
