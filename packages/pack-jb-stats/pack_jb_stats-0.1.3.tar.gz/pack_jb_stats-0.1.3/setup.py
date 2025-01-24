from setuptools import setup, find_packages

setup(
    name='pack_jb_stats',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'scipy',
        'numpy',  # Ajoutez d'autres dépendances nécessaires ici
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

)
 

