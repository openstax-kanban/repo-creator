from setuptools import setup

requires = ['docopt', 'github3.py']

setup(
    name='issue-importer',
    version='0.0.1',
    description='',
    long_description='',
    url='https://github.com/openstax-kanban/repo-creator',
    license='AGPLv3',
    author='m1yag1',
    author_email='qa@openstax.org',
    py_modules=['creator'],
    install_requires=requires,
    zip_safe=False,
    entry_points={
        'console_scripts': ['imp=importer:cli']
    },
    classifiers=[],
)
