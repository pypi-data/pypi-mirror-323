# setup.py
from setuptools import setup, find_packages
import platform

def get_all_dependencies():
    # Core dependencies
    dependencies = [
        "numpy>=1.22.0,<2.1.0",  # Last 1.x version that works well with TF 2.18
        "PyOpenGL==3.1.7",
        "PyOpenGL-accelerate==3.1.7",
        "scipy==1.14.1",
        "matplotlib==3.10.0",
        "pandas==2.2.3",
        "pygame==2.6.1",
        
        # ML stack with compatible versions
        "tensorflow==2.18.0",
        "tensorflow-io-gcs-filesystem==0.31.0",
        "keras==3.7.0",
        "scikit-learn==1.6.0",
        "tensorboard==2.18.0",
        "tensorboard-data-server==0.7.2",
        "shap==0.46.0",
        "numba==0.60.0",
        
        # Utilities and dependencies
        "absl-py==2.1.0",
        "astunparse==1.6.3",
        "cloudpickle==3.1.0",
        "contourpy==1.3.1",
        "cycler==0.12.1",
        "flatbuffers==24.3.25",
        "fonttools==4.55.3",
        "gast==0.4.0",
        "google-pasta==0.2.0",
        "grpcio==1.68.1",
        "h5py==3.12.1",
        "joblib==1.4.2",
        "kiwisolver==1.4.7",
        "libclang==18.1.1",
        "llvmlite==0.43.0",
        "ml-dtypes==0.4.1",
        "opt_einsum==3.4.0",
        "optree==0.13.1",
        "packaging==24.2",
        "protobuf==3.20.3",
        "six==1.17.0",
        "slicer==0.0.8",
        "termcolor==2.5.0",
        "threadpoolctl==3.5.0",
        "typing_extensions==4.12.2",
        "wrapt==1.17.0",
        
        # Development and documentation
        "Markdown==3.7",
        "Pygments==2.18.0",
        "rich==13.9.4",
        "docutils==0.21.2",
        
        # Additional utilities
        "colorama==0.4.6",
        "pytz==2024.2",
        "tzdata==2024.2",
        "urllib3==2.2.3",
        "Werkzeug==3.1.3",
        "zipp==3.21.0"
    ]
    
    # Platform-specific dependencies
    if platform.system().lower() == 'windows':
        dependencies.extend([
            "pywin32-ctypes==0.2.3",
            "backports.tarfile==1.2.0"
        ])
    
    return dependencies

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quantum_dot_sim",
    version="2.1.1",
    author="Arjun Skanda Ananda",
    author_email="arjunskanda@yahoo.com",
    license="MIT",
    description="A package for simulating quantum dot behavior and analyzing energy levels, absorption spectra, and wavefunctions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArjunSkanda/quantum_dot_sim",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7,<3.11",
    install_requires=get_all_dependencies(),
    entry_points={
        "console_scripts": [
            "quantum-dot-sim=demo:main",
        ],
    },
)