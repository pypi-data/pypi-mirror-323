from setuptools import setup, find_packages

setup(
    name='anifetch',
    version='0.1.0',
    author='Shoaib Hossain',  
    author_email='sh.shoaib8@gmail.com',
    description='Clone of neofetch but with anime characters as ascii arts',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown', 
    url='https://github.com/KillerShoaib/Anifetch',  
    packages=find_packages(), 
    install_requires=[
        'rich==13.7.1',
    ],
    entry_points={
        'console_scripts': [
            'anifetch = Anifetch:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.7',
)