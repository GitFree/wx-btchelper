#encoding=utf-8
from fetcher import *


def file_handler_max():
    for i in xrange(10000):
        mt = Fetcher(str(i))

if __name__ == '__main__':
    file_handler_max()
