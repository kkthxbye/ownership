"""
Integration tests.
"""

import unittest
from ownership.manager import Manager
from ownership.resource import Resource
from ownership.client import Client


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()
        self.resources = [Resource(x) for x in range(10)]
        self.manager.resources = self.resources

    def test_empty(self):
        self.assertEqual({}, self.manager.allocation)

    def test_provided(self):
        S1 = self.make_client(1, [2, 3])
        S2 = self.make_client(2, [2, 4, 5])
        S3 = self.make_client(3, [2])
        S4 = self.make_client(4, [2, 3], Client.PRIORITY_LOW)

        self.manager.add(S1)
        self.assertEqual(
            self.map_desired({
                2: S1,
                3: S1,
            }), self.manager.allocation)

        self.manager.add(S2)
        self.assertEqual(
            self.map_desired({
                2: S1,
                3: S1,
                4: S2,
                5: S2,
            }), self.manager.allocation)

        self.manager.add(S3)
        self.assertEqual(
            self.map_desired({
                2: S3,
                3: S1,
                4: S2,
                5: S2,
            }), self.manager.allocation)

        self.manager.revoke(S2)
        self.assertEqual(
            self.map_desired({
                2: S3,
                3: S1,
            }), self.manager.allocation)

        self.manager.add(S4)
        self.assertEqual(
            self.map_desired({
                2: S3,
                3: S1,
            }), self.manager.allocation)

    def test_uniform(self):
        S1 = self.make_client(1, [1, 2, 3])
        S2 = self.make_client(2, [2, 3, 4])
        S3 = self.make_client(3, [1, 2, 3, 4, 5, 6])

        self.manager.add(S1)
        self.assertEqual(
            self.map_desired({
                1: S1,
                2: S1,
                3: S1,
            }), self.manager.allocation)

        self.manager.add(S2)
        self.assertEqual(
            self.map_desired({
                1: S1,
                2: S1,
                3: S2,
                4: S2,
            }), self.manager.allocation)

        self.manager.add(S3)
        self.assertEqual(
            self.map_desired({
                1: S1,
                2: S1,
                3: S2,
                4: S2,
                5: S3,
                6: S3,
            }), self.manager.allocation)

    def test_lowprio(self):
        S1 = self.make_client(1, [1, 2])
        S2 = self.make_client(2, [2, 3, 4], Client.PRIORITY_LOW)

        self.manager.add(S1)
        self.assertEqual(self.map_desired({
            1: S1,
            2: S1,
        }), self.manager.allocation)

        self.manager.add(S2)
        self.assertEqual(self.map_desired({
            1: S1,
            2: S1,
            3: S2,
            4: S2,
        }), self.manager.allocation)

    def map_desired(self, d):
        return {self.resources[key]: x for key, x in d.items()}

    def make_client(self, _id, resource_ids, priority=Client.PRIORITY_NORMAL):
        client = Client(_id)
        client.claimed = [self.resources[x] for x in resource_ids]
        client.priority = priority
        return client


if __name__ == '__main__':
    unittest.main()
