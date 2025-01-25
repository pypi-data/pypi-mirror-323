from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='hyypns',
    version='0.0.3',
    description='hyypns',
    long_description=long_description,
    author='huang yi yi',
    author_email='363766687@qq.com',
    py_modules=['hyypns'],
    include_package_data=True,
    python_requires='>=3.6',
)