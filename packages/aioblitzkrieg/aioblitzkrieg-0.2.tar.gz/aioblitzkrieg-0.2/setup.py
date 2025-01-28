from setuptools import setup, find_packages

with open('requirements.txt', 'r', encoding='utf-16') as f:
    requires =[r.split('=')[0] for r in f.read().splitlines()]

print(requires)

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='aioblitzkrieg',
    version='0.2',    
    description='@BlitzkriegAutobot asynchronous api wrapper',
    url='https://github.com/bblitzKrieg/aioblitzkrieg',
    author='Blitzkrieg',
    author_email='blitzkriegdev@blitzkrieg.space',
    license='BSD 2-clause',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=requires,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)