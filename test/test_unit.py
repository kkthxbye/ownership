import unittest
import ownership
from ownership.manager import Manager
from ownership.client import Client
from ownership.resource import Resource
from ownership.allocation import Uniform


class OwnershipTestCommon(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()
        self.resources = [Resource(x) for x in range(10)]
        self.manager.resources = self.resources

    def make_client(self, _id, resource_ids, priority=Client.PRIORITY_NORMAL):
        client = Client(_id)
        client.claimed = self.resources_by_ids(resource_ids)
        client.priority = priority
        return client

    def make_claim(self, client, resource_ids):
        return (client, [self.resources[x] for x in resource_ids])

    def resources_by_ids(self, ids):
        return [self.resources[x] for x in ids]


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


class ManagerTest(OwnershipTestCommon):
    def setUp(self):
        super(ManagerTest, self).setUp()
        self.clients_count = 3
        self.resources_count = 5

        self.manager = Manager()
        self.resources = [Resource(x) for x in range(self.resources_count)]
        self.manager.resources = self.resources
        self.clients = [
            self.make_client(x + 1, [x + 1])
            for x in range(self.clients_count)
        ]
        for client in self.clients:
            self.manager.add(client)

    def map_allocation(self, d):
        return {self.resources[key]: x for key, x in d.items()}

    def test_add(self):
        client = Client(self.clients_count + 1)
        client.claimed = [self.resources[self.clients_count + 1]]

        allocation = self.manager.add(client)

        self.assertEqual(
            self.map_allocation({
                1: self.clients[0],
                2: self.clients[1],
                3: self.clients[2],
                4: client,
            }), allocation)

    def test_revoke(self):
        allocation = self.manager.revoke(self.clients[0])

        self.assertEqual(
            self.map_allocation({
                2: self.clients[1],
                3: self.clients[2],
            }), allocation)

    def test_get_open_claims(self):
        claims = self.manager.get_open_claims([self.resources[1]])

        self.assertEqual([
            (self.clients[1], [self.resources[2]]),
            (self.clients[2], [self.resources[3]]),
        ], claims)

    def test_get_claimed_resources(self):
        self.assertEqual(
            set([
                self.resources[1],
                self.resources[2],
                self.resources[3],
            ]), self.manager.get_claimed_resources())

    def test_reassign(self):
        allocation = self.manager.reassign({
            1: self.clients[2],
            2: self.clients[1],
        })

        self.assertEqual({
            2: self.clients[1],
            1: self.clients[2],
        }, allocation)

    def test_allocate(self):
        allocation = self.manager.allocate()
        self.assertEqual(
            self.map_allocation({
                1: self.clients[0],
                2: self.clients[1],
                3: self.clients[2],
            }), allocation)


if __name__ == '__main__':
    unittest.main()
