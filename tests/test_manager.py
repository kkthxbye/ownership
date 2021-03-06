import unittest
from ownership.client import Client
from .common import OwnershipTestCommon


class ManagerTest(OwnershipTestCommon):
    def setUp(self):
        super(ManagerTest, self).setUp()
        self.clients_count = 3

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
