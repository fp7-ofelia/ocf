import sys
#import unittest
try:
    import unittest2 as unittest
except:
    import unittest 

class TestCase(unittest.TestCase):
    def runTest(self):
        """
        Explicitly call tests in order to be invoked through test suite.
        """
        # Dynamic retrieval of tests in module (methods starting with "test_")
        existing_tests = filter(lambda x: x.startswith("test_"), dir(self))
        for existing_test in existing_tests:
            # Invoke each test method
            getattr(self, existing_test)()

##
# Helper methods
#

def test_main():
    """
    Counts errors and successes from tests.
    """
    try: 
        test = unittest.main(verbosity=2, exit=False)
    except:
        test = unittest.main()
    # Retrieve errors
    #test_passed = test.result.wasSuccessful()
    #test_total = test.result.testsRun
    test_errors = len(test.result.errors)
    test_failures = len(test.result.failures)
    # Return code for exiting program with it
    test_result = True if test_errors + test_failures == 0 else False
    return test_result

def main():
    """
    Return errors and successes when directly invoked.
    """
    if len(sys.argv) == 2:
        arg = sys.argv[1]
    del sys.argv[1:]
    # sys.exit with code to notify Jenkins about validity (or not) of tests
    test_result = test_main()
    # Inverse logic for tests => 0: OK, 1: ERROR
    test_result = int(not(test_result))
    print test_result
    sys.exit(test_result)
