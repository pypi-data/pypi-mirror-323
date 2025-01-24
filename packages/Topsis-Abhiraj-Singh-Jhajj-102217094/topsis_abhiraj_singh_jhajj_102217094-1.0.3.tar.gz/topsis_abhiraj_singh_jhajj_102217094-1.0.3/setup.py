from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='Topsis_Abhiraj_Singh_Jhajj_102217094',
    version='1.0.3',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.19.0',
    ],
    author='Abhiraj Singh Jhajj',
    description='A Python package for performing TOPSIS analysis.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='topsis multi-criteria decision-making ranking analysis',
    project_urls={
        'Documentation': 'https://github.com/abhirajsinghjhajj/Topsis_Abhiraj_Singh_Jhajj_102217094/blob/main/README.md',
        'Source': 'https://github.com/Topsis_Abhiraj_Singh_Jhajj_102217094/Topsis-Package',
    },
    python_requires='>=3.7',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'topsis=Topsis_Abhiraj_Singh_Jhajj_102217094.main:main',
        ],
    },
)
