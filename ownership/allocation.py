"""Allocation stategies
"""
from abc import ABC, abstractmethod
from .client import Client
from .resource import Resource


class AllocationStrategy(ABC):
    """
    Decides which client-resource
    pair has to be picked given certain state of
    open claims and existing allocations

    Attributes:

        claims: [Client, [Resource]] currently open claims

        allocation: {Resource, Client}

    """

    def __init__(self, claims, allocation):
        self.claims = claims
        self.allocation = allocation

    @abstractmethod
    def pick_pair(self) -> (Resource, Client):
        """Given present state pick resource-client pair
        """
        pass

    @classmethod
    def priority_claims(cls, claims) -> [Client, [Resource]]:
        """Get current priority claims
        """
        # First bother about the important guys
        priority_claims = [(client, resources) for client, resources in claims
                           if client.priority != Client.PRIORITY_LOW]

        # If there are no important guys - promote LOWPRIO
        return priority_claims if priority_claims else claims

    def get_allocation_by_client(self) -> [Client, [Resource]]:
        """Get current allocation grouped by client
        """
        allocation = {}
        for resource, client in self.allocation.items():
            allocation.setdefault(client, []).append(resource)

        return allocation

    def get_least_claimed_resources_queue(self) -> [Resource]:
        """Get resources ordered by the descending amount of claims
        """
        queue = {}
        for client, resources in self.claims:
            for resource in resources:
                queue.setdefault(resource, []).append(client)

        return [
            resource for resource, client in sorted(
                queue.items(), key=lambda x: len(x[1]))
        ]


class Uniform(AllocationStrategy):
    """Aims towards uniform distribution of resources across clients.
    """

    def default_claims_queue(self) -> [Client, [Resource]]:
        return self.deprived_claims(self.priority_claims(self.claims))

    def deprived_claims(self, claims) -> [Client, [Resource]]:
        """Get claims excluding those who reached their current max
        """
        allocation_by_client = self.get_allocation_by_client()
        max_allocation_count = max(
            (len(x) for x in allocation_by_client.values()), default=0)

        deprived_claims = [
            (client, resources) for client, resources in claims
            if len(allocation_by_client.get(client, [])) < max_allocation_count
        ]

        # Not having any claims at this point means
        # they are all equally deprived
        return deprived_claims if deprived_claims else claims

    def pick_pair(self):
        claims = self.default_claims_queue()
        # Claimed resources ordered by the least amount of claims
        uniform_queue = [(resource, [
            client for client, claimed_resources in claims
            if resource in claimed_resources
        ]) for resource in self.get_least_claimed_resources_queue()]

        # Filter out resources we cannot allocate yet.
        uniform_queue = [(resource, clients)
                         for resource, clients in uniform_queue
                         if len(clients)]

        resource, clients = uniform_queue[0]
        return resource, clients[0]
