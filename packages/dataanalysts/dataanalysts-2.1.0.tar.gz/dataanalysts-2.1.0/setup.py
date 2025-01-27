# setup.py
from setuptools import setup, find_packages

setup(
    name='dataanalysts',
    version='2.1.0',
    description = 'A powerful Python library designed to simplify data analysis by providing one-line solutions for cleaning, transformation, and visualization. Eliminate boilerplate code with intuitive, feature-rich functions tailored for analysts, researchers, and developers. Streamline workflows with advanced preprocessing and insightful visualizations, all in a single, user-friendly package.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Venkata Govind Neelapu',
    author_email='venkatagovindneelapu@gmail.com',
    license='MIT',
    url='https://github.com/yourusername/dataanalysts',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'scikit-learn',
        'seaborn'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)




