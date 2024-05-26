import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))

from run import celery

if __name__ == '__main__':
    celery.start()