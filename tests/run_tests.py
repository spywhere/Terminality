import sys
import unittest
from os.path import dirname, join, abspath


HERE = dirname(__file__)
from_here = lambda *parts: abspath(join(HERE, *parts))
sys.path += [
    from_here("..", "..")
]


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(HERE)

    unittest.TextTestRunner(
        verbosity=5
    ).run(suite)


if __name__ == "main":
    main()
