"""Resource allocation manager
"""
from .client import Client
from .resource import Resource
from .allocation import Uniform


class Manager:
    """
    Manages "resource: client" assignation

    Attributes:

        resources: [Resource] initialized resources

        clients: [Client] current clients

        allocation: {Client: Resource} current client-resource assignations
    """

    def __init__(self):
        self.resources = []
        self.clients = []
        self.allocation = {}

    def add(self, client: Client) -> {Resource: Client}:
        """Add client reallocating resources accordingly
        """
        self.clients.append(client)
        return self.allocate()

    def revoke(self, client: Client) -> {Resource: Client}:
        """Revoke client's claims reallocating resources accordingly
        """
        self.clients = [x for x in self.clients if x != client]
        return self.allocate()

    def allocate(self) -> {Client: [Resource]}:
        """Perform allocation based on selected strategy
        """
        new_allocation = {}
        for _ in self.get_claimed_resources():
            claims = self.get_open_claims(new_allocation.keys())

            served_resource, served_client = Uniform(
                claims, new_allocation).pick_pair()

            new_allocation[served_resource] = served_client

        return self.reassign(new_allocation)

    def reassign(self, new_allocation) -> {Resource: Client}:
        """Perform mutable reassignation on existing allocation
        """
        diff = (k for k in set(
            list(self.allocation.keys()) + list(new_allocation.keys()))
                if self.allocation.get(k) != new_allocation.get(k))

        for resource in diff:
            if resource in self.allocation:
                del self.allocation[resource]
            if resource in new_allocation:
                self.allocation[resource] = new_allocation.get(resource)

        return self.allocation

    def get_open_claims(self, excluded_resources) -> [Client, [Resource]]:
        """Get current claims without "excluded_resources"
        """
        claims = ((client, [
            resource for resource in client.claimed
            if resource not in excluded_resources
        ]) for client in self.clients)

        return [(client, resources) for client, resources in claims
                if len(resources)]

    def get_claimed_resources(self) -> set([Resource]):
        """Get resources claimed by current clients
        """
        return set(
            resource for client in self.clients for resource in client.claimed)
