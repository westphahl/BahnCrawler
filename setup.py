from distutils.core import setup
try:
    import py2exe
except ImportError:
    pass

setup(
    name="BahnCrawler",
    author="Simon Westphahl",
    author_email="westphahl@gmail.com",
    packages=['bahncrawler', 'bahncrawler.utils'],
    scripts=['bahn_crawler.py'],
    console=['bahn_crawler.py'], # py2exe
    options={
        'py2exe': {
            'includes': ['greenlet', ]
        }
    }
)
