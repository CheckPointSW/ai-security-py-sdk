import unittest
import os

if os.path.exists('./.env'):
    from dotenv import load_dotenv
    load_dotenv()


class GlobalTest(unittest.TestCase):
    pass
