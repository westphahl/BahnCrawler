from distutils.core import setup
import py2exe

setup(
    console=['bahn_crawler.py'],
    options={
        'py2exe': {
            'includes': ['greenlet',]
        }
    }
)
