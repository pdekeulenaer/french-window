import unittest
import test_schema, test_models, test_db

if __name__ == '__main__':
    suites = []
    suites.append(test_schema.suite())
    suites.append(test_models.suite())
    suites.append(test_db.suite())
    suite = unittest.TestSuite(suites)

    unittest.TextTestRunner(verbosity=2).run(suite)


