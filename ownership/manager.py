from typing import Dict, List, Set

from ownership.allocation import Uniform
from ownership.client import Client
from ownership.resource import Resource


class Manager:
    """
    Manages "resource: client" assignation.

    Attributes:
        resources: List[Resource] initialized resources
        clients: List[Client] current clients
        allocation: Dict[Client, Resource] current client-resource assignations
        strategy: AllocationStrategy strategy to be used for allocation

    """

    def __init__(self) -> None:
        self.resources = []
        self.clients = []
        self.allocation = {}
        self.strategy = Uniform

    def add(self, client: Client) -> Dict[Resource, Client]:
        """Add client reallocating resources accordingly."""
        self.clients.append(client)
        return self.allocate()

    def revoke(self, client: Client) -> Dict[Resource, Client]:
        """Revoke client's claims reallocating resources accordingly."""
        self.clients.remove(client)
        return self.allocate()

    def allocate(self) -> Dict[Client, List[Resource]]:
        """Perform allocation based on selected strategy."""
        new_allocation = {}
        for _ in self.get_claimed_resources():
            claims = self.get_open_claims(new_allocation.keys())

            served_resource, served_client = self.strategy(
                claims, new_allocation).pick_pair()

            new_allocation[served_resource] = served_client

        return self.reassign(new_allocation)

    def reassign(self, new_allocation) -> Dict[Resource, Client]:
        """Perform mutable reassignation on existing allocation."""
        diff = (k for k in set(
            list(self.allocation.keys()) + list(new_allocation.keys()))
            if self.allocation.get(k) != new_allocation.get(k))

        for resource in diff:
            if resource in self.allocation:
                del self.allocation[resource]
            if resource in new_allocation:
                self.allocation[resource] = new_allocation.get(resource)

        return self.allocation

    def get_open_claims(self, excluded_resources) -> List[Client, List[Resource]]:
        """Get current claims without "excluded_resources"."""
        claims = ((client, [
            resource for resource in client.claimed
            if resource not in excluded_resources
        ]) for client in self.clients)

        return [(client, resources) for client, resources in claims
                if len(resources)]

    def get_claimed_resources(self) -> Set[Resource]:
        """Get resources claimed by current clients."""
        return set(
            resource for client in self.clients for resource in client.claimed)
