from setuptools import setup, find_packages

setup(
    name='DeepParameters',
    version='0.0.5',
    author='Your Name',
    author_email='rudzani.mulaudzi2@students.wits.ac.za',
    description='A package for learning CPDs using deep learning models',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/rudzanimulaudzi/DeepParameters',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'pgmpy',
        'scipy',
        'scikit-learn',
        'tensorflow',
        'matplotlib',
        'networkx',
        'keras',
        'tensorflow-probability'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)