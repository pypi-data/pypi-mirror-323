# from setuptools import setup, find_packages

# setup(
    # name="Dossenge",
    # version="0.1",
    # description="My First Package",
    # packages=find_packages(),
    # python_requires='>=3.0',
# )

from setuptools import setup, find_packages

setup(
    name='Dossenge',
    version='0.5.2.post3',
    description='Dossenge 0.5.2.post3',
    long_description=open('README.md','r',encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Dossenge',
    # url='http://your.package.home.page',
    packages=find_packages(),  # Include all packages, subpackages and modules
    install_requires=[
        # List of dependencies
        'toml',
    ],
    # classifiers=[
        # 'Development Status :: 3 - Alpha',
        # 'Intended Audience :: Developers',
        # 'License :: OSI Approved :: MIT License',
        # 'Programming Language :: Python :: 3',
    # ],
    python_requires='>=3.0',
    entry_points={
        'console_scripts': [
            'dossenge = Dossenge.Dossenge:dossenge',
        ],
    },
)
