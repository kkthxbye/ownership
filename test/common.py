import unittest
from ownership.manager import Manager
from ownership.resource import Resource
from ownership.client import Client


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
