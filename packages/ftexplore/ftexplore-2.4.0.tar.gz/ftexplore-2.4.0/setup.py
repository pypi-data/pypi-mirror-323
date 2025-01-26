import os
import setuptools
import shutil


with open(os.path.join(os.path.dirname(__file__), '..', 'README.md'), 'r') as f:
    long_description = f.read()

setup_kwargs = {
    'name': 'ftexplore',
    'version': '2.4.0',
    'author': 'Dirk Henrici',
    'author_email': 'ftexplore@henrici.name',
    # Control fischertechnik models using RaspberryPi hardware with a graphical user interface and Python scripts
    'description': 'ft-Explore allows to control motors and to check inputs by GUI and user-provided Python code',
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',
    'url': 'https://www.henrici.name/projects/ftexplore.html',
    'packages': setuptools.find_packages(),
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop'
    ],
    'python_requires': '>=3.5',
    #'install_requires': [
    #      'cffi',
    #      'pynng',
    #],
    'extras_require': {
        'remote':  ['cffi', 'pynng', 'keyboard'],        
    },
    'keywords': 'motorhat raspberrypi fischertechnik education',
    'project_urls': {
        'German Homepage': 'https://www.henrici.name/projects/ftexplore.html',
        'Repository': 'https://www.hosting-srv.de/gitea/HNET/ftexplore/',
        'Source': 'https://www.hosting-srv.de/gitea/HNET/ftexplore/src/branch/master/src',
    },
}


def copy_files():
    setupdir = os.path.dirname(__file__)
    rootdir = os.path.join(setupdir, '..')
    shutil.copyfile(os.path.join(rootdir, 'README.md'), os.path.join(setupdir, 'README.md'))
    shutil.copyfile(os.path.join(rootdir, 'LICENSE'), os.path.join(setupdir, 'LICENSE.txt'))


if __name__ == '__main__':
    copy_files()
    setuptools.setup(**setup_kwargs)
