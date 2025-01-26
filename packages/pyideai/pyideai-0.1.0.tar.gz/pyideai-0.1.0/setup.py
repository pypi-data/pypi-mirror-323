from setuptools import setup, find_packages

setup(
    name='pyideai',
    version='0.1.0',
    author='Mehmet Utku ÖZTÜRK',
    author_email='mutkuoz@proton.me',
    description='A module to interact with ideai.dev using Selenium WebDriver.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/mutkuoz/pyideai',  
    packages=find_packages(),
    install_requires=[
        'selenium',
        'beautifulsoup4',
        'webdriver-manager',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
) 