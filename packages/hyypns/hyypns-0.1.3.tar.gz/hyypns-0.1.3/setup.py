from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='hyypns',
    version='0.1.3',
    description='hyypns',
    long_description=long_description,
    author='huang yi yi',
    author_email='363766687@qq.com',
    py_modules=['hyypns'],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        'pyfiglet>=1.0.1.post1',
        "requests>=2.32.2.post1",
        'Cython>=3.0.11',
        'setuptools>=75.7.0',
        'pillow>=11.0.0',
        'WMI>=1.5',
        'docker>=7.0.0',
    ],
)