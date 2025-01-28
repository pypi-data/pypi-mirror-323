from setuptools import setup, find_packages

setup(
    name='UzSonSoz',
    version='1.0',
    author='dasturbek',
    author_email='sobirovogabek0409@gmail.com',
    description='O‘zbek tilida sonlarni so‘zga, so‘zlarni esa songa almashtiruvchi dastur.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ddasturbek/UzSonSoz',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
