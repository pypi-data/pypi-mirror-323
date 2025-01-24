import setuptools

with open("README.md","r",encoding="utf-8") as fi:
    long_description = fi.read()

setuptools.setup(
    name="TFInterpy",
    version="1.1.3",
    author="Zhiwen Chen",
    author_email="orchenz@qq.com",
    description="TFInterpy is a Python package for spatial interpolation. A high-performance version of several interpolation algorithms is implemented based on TensorFlow. Including parallelizable IDW and Kriging algorithms. So far, tfinterpy is the **fastest open source Kriging** algorithm, which can reduce the operation time of large-scale interpolation tasks by an order of magnitude.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/czwchenzhun/tfinterpy.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy==2.0.2',
        'scipy==1.13.1',
    ]
)