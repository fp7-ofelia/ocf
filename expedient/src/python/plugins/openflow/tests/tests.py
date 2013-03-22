'''
Created on May 19, 2010

@author: jnaous
'''

TESTS=["gapi/gapi.py", "full/fulltests.py", "om/om.py"]

if __name__ == '__main__':
    import subprocess
    from os.path import dirname, join
    for t in TESTS:
        file = join(dirname(__file__), t) 
        subprocess.call(["python", file])
