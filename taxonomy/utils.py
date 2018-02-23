"""Helpers for Taxonomy module."""
from taxonomy.models import (
    Taxon, HbvName, HbvFamily, HbvGenus, HbvSpecies, HbvXref)

def update_taxon():
    """Update Taxon from Hbv data.
    """

    # Domain Eukarya
    domain, created = Taxon.objects.get_or_create(name_id=0, name="Eukarya", rank=Taxon.RANK_DOMAIN)

    # Kindoms of Eukarya
    [Taxon.objects.get_or_create(
        name_id=x.name_id, 
        name=x.name, 
        rank=Taxon.RANK_KINGDOM,
        parent = domain) 
        for x in HbvName.objects.filter(rank_name='Kingdom')]