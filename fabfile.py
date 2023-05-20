from invoke import run
from invoke.context import Context
import sys

# i had to change it because i had error and after researtch i found that the fabric v1 syntax can not work with my v2 
def test():
    c = Context()
    c.config.run.warn = True
    result = run("python test_tasks.py -v && python test_users.py -v")
    if result.failed:
        if not input("Tests failed. Continue? [y/N] ").lower().startswith('y'):
            sys.exit("Aborted at user request.")