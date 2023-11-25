import unittest
from timelineData import *

class TestGanttDatabase(unittest.TestCase):
    def setUp(self):
        # Create an instance of GanttDatabase for testing
        pass

    def tearDown(self):
        # Clean up any resources used during the test
        pass

    def test_overlap_algorithm_0(self):
        definition = {}
        definition['title'] = 'Test'
        definition['data'] = [
            {
                'label': 'Test',
                'start': 0,
                'end': 2,
                'column': 0
            },
            {
                'label': 'Test',
                'start': 1,
                'end': 3,
                'column': 0
            },
            {
                'label': 'Test',
                'start': 4,
                'end': 5
            }
        ]

        database = GanttDatabase(definition)

        self.assertEqual(database.maxOverlaps, 1)

    def test_overlap_algorithm_1(self):
        definition = {}
        definition['title'] = 'Test'
        definition['data'] = [
            {
                'label': 'Test',
                'start': 0,
                'end': 2,
                'column': 1
            },
            {
                'label': 'Test',
                'start': 1,
                'end': 5,
                'column': 0
            },
            {
                'label': 'Test',
                'start': 3,
                'end': 6
            },
            {
                'label': 'Test',
                'start': 4,
                'end': 8,
                'column': 0
            },
            {
                'label': 'Test',
                'start': 7,
                'end': 9,
                'column': 1
            }
        ]

        database = GanttDatabase(definition)

        self.assertEqual(database.maxOverlaps, 2)
    
    def test_overlap_algorithm_2(self):
        definition = {}
        definition['title'] = 'Test'
        definition['data'] = [
            {
                'label': 'Test',
                'start': 0,
                'end': 2,
                'column': 1
            },
            {
                'label': 'Test',
                'start': 1,
                'end': 5,
                'column': 0
            },
            {
                'label': 'Test',
                'start': 3,
                'end': 6
            },
            {
                'label': 'Test',
                'start': 4,
                'end': 8,
                'column': 0
            },
            {
                'label': 'Test',
                'start': 7,
                'end': 9,
                'column': 1
            },
            {
                'label': 'Test',
                'start': 10,
                'end': 12,
                'column': 1
            },
            {
                'label': 'Test',
                'start': 11,
                'end': 13,
                'column': 0
            },
            {
                'label': 'Test',
                'start': 14,
                'end': 15
            }
        ]

        database = GanttDatabase(definition)

        self.assertEqual(database.maxOverlaps, 2)