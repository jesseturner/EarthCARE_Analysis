from setuptools import setup, find_packages

packages=find_packages()
print("Found packages:", packages)

setup(
    name='earthcare_plot',
    version='0.1',
    packages=packages,
    install_requires=[
        'matplotlib', 'numpy', 'h5py', 'cartopy', 'xarray', 'netcdf4'
        ],
    python_requires='>=3.7',
    author='Jesse Turner',
    description='A tool for plotting EarthCARE products and ground tracks.',
    url='https://github.com/jesseturner/EarthCARE_Analysis',
)