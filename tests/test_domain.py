import copy
import unittest
from app import domain
from app.service import load_study


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.data = load_study()
        self.request = {'operation': 'repeatability', 'instrument': 'meter-1'}

    def test_range_of_two_readings(self):
        data = copy.deepcopy(self.data)
        data['readings'] = [dict(data['readings'][0], value=10, replicate=1),
                            dict(data['readings'][0], value=14, replicate=2)]
        result = domain.act(data, self.request)['repeatability'][0]
        self.assertEqual(result['mean'], 12)
        self.assertEqual(result['range'], 4)

    def test_duplicate_reading_is_rejected(self):
        data = copy.deepcopy(self.data)
        data['readings'].append(data['readings'][0])
        with self.assertRaises(ValueError):
            domain.baseline(data)

    def test_unit_mismatch(self):
        data = copy.deepcopy(self.data)
        data['readings'][0]['unit'] = 'unknown'
        with self.assertRaises(ValueError):
            domain.baseline(data)


if __name__ == '__main__':
    unittest.main()
