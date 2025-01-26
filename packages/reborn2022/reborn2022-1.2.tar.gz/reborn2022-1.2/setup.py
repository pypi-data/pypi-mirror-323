from setuptools import setup, find_packages
with open('requirements.txt') as f:
    required_packages = f.readlines()

required_packages = [pkg.strip() for pkg in required_packages]
setup(
    name='reborn2022',
    version='1.2',
    packages=find_packages(),
    install_requires=required_packages,
    author='PetapaGenit',
    author_email='khaerudin2119@gmail.com',
    description='Paket python untuk menyelesaikan recaptchav2',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/xnoxs-dev/reborn2022',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
