from distutils.core import setup
from version import get_git_version

setup(
    name='Voixer',
    version=get_git_version(),
    packages=['voixer'],
    url='http://codetalk.io/',
    license='BSD',
    author='Christian Laustsen, Martin Madsen',
    author_email='christianlaustsen@gmail.com, martin@martinjlowm.dk',
    description='A VoIP/IM communication server.'
)
