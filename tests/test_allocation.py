import unittest

from ownership.allocation import Uniform
from ownership.client import Client

from test.common import OwnershipTestCommon


class UniformAllocationTest(OwnershipTestCommon):
    def setUp(self):
        super(UniformAllocationTest, self).setUp()
        self.clients = [
            self.make_client(1, [2, 3]),
            self.make_client(3, [2]),
            self.make_client(4, [2, 3], Client.PRIORITY_LOW),
        ]
        self.claims = [
            self.make_claim(self.clients[0], [2, 3]),
            self.make_claim(self.clients[1], [2]),
            self.make_claim(self.clients[2], [2, 3]),
        ]
        self.allocation = {
            self.resources[3]: self.clients[0],
        }

        self.uniform = Uniform(self.claims, self.allocation)

    def test_priority_claims(self):
        self.assertEqual([
            self.make_claim(self.clients[0], [2, 3]),
            self.make_claim(self.clients[1], [2]),
        ], self.uniform.priority_claims(self.claims))

    def test_get_allocation_by_client(self):
        self.assertEqual({
            self.clients[0]: self.resources_by_ids([3]),
        }, self.uniform.get_allocation_by_client())

    def test_get_least_claimed_resources_queue(self):
        self.assertEqual(
            self.resources_by_ids([
                3,
                2,
            ]), self.uniform.get_least_claimed_resources_queue())

    def test_deprived_claims(self):
        self.assertEqual([
            self.make_claim(self.clients[1], [2]),
            self.make_claim(self.clients[2], [2, 3]),
        ], self.uniform.deprived_claims(self.claims))

    def test_default_claims_queue(self):
        self.assertEqual([(self.resources[2], [
            self.clients[1],
        ])], self.uniform.get_queue())

    def test_pick_pair(self):
        resource, client = self.uniform.pick_pair()
        self.assertEqual(self.resources[2], resource)
        self.assertEqual(self.clients[1], client)
