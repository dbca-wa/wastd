"""Helpers for Taxonomy module."""
import logging
# from pdb import set_trace
from django.db import transaction
from taxonomy.models import (Taxon, HbvName, HbvFamily, HbvGenus, HbvSpecies)  # HbvXref

logger = logging.getLogger(__name__)


def make_family(fam, kingdom_dict, current_dict, publication_dict):
    """Create Taxon nodes for Division, Class, Order and Family from a HbvFamily record.

    Arguments

    fam An object instance of HBvFamily
    kingdom_dict A lookup of Kingdom IDs and corresponding Taxa of rank Kingdom.
    publication_dict A lookup for publication_status
    current_dict A lookup for current
    """
    lowest_parent = kingdom_dict[fam.kingdom_id]

    if fam.division_nid:
        dd = dict(
            name_id=fam.division_nid,
            name=fam.division_name,
            rank=Taxon.RANK_DIVISION,
            parent=lowest_parent)
        division, created = Taxon.objects.update_or_create(name_id=fam.division_nid, defaults=dd)
        lowest_parent = division
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, division))

    if fam.class_nid:
        dd = dict(
            name_id=fam.class_nid,
            name=fam.class_name,
            rank=Taxon.RANK_CLASS,
            parent=lowest_parent)
        clazz, created = Taxon.objects.update_or_create(name_id=fam.class_nid, defaults=dd)
        lowest_parent = clazz
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, clazz))

    if fam.order_nid:
        dd = dict(
            name=fam.order_name,
            rank=Taxon.RANK_ORDER,
            parent=lowest_parent)
        order, created = Taxon.objects.update_or_create(name_id=fam.order_nid, defaults=dd)
        lowest_parent = order
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, order))

    dd = dict(name=fam.family_name,
              rank=Taxon.RANK_FAMILY,
              current=current_dict[fam.is_current],
              parent=lowest_parent,
              author=fam.author)
    if fam.informal is not None:
        dd['publication_status'] = publication_dict[fam.informal]
        print(dd['publication_status'])
    family, created = Taxon.objects.update_or_create(name_id=fam.name_id, defaults=dd)
    action = "Created" if created else "Updated"
    logger.info("[make_family] {0} {1}.".format(action, family))

    return family


def make_genus(x, current_dict, publication_dict, taxon_dict):
    """Create or update a Taxon of rank Genus.

    Arguments

    x An instance of HbvGenus
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict of parent Family name_id to Taxon instance

    Return The created or updated instance of Taxon.
    """
    dd = dict(
        name=x.genus,
        rank=Taxon.RANK_GENUS,
        current=current_dict[x.is_current],
        parent=taxon_dict[x.family_nid],
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    obj.parent__id = x.family_nid
    obj.save()
    action = "Created" if created else "Updated"

    logger.info("[make_genus] {0} {1}.".format(action, obj))
    return obj


def make_species(x, current_dict, publication_dict, taxon_dict):
    """Create or update a Taxon of rank Species.

    Arguments

    x An instance of HbvSpecies, rank_name "Species"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict of parent Genus name to Taxon instance

    Return The created or updated instance of Taxon.
    """
    dd = dict(
        name=x.species,
        rank=Taxon.RANK_SPECIES,
        current=current_dict[x.is_current],
        parent=taxon_dict[x.genus],
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_species] {0} {1}.".format(action, obj))
    return obj


def make_subspecies(x, current_dict, publication_dict, taxon_dict):
    """Create or update a Taxon of rank Subspecies.

    Arguments

    x An instance of HbvSpecies, rank_name "Subspecies"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict for parent species name to Taxon instance

    Return The created or updated instance of Taxon.
    """
    try:
        parent = taxon_dict[x.species]
    except KeyError:
        logger.warn("[make_variety] Couldn't find record for subspecies "
                    "{0}, using genus {1} as parent".format(x.infra_name, x.genus))
        parent = Taxon.objects.get(name=x.genus)
    dd = dict(
        name=x.infra_name,
        rank=Taxon.RANK_SUBSPECIES,
        current=current_dict[x.is_current],
        parent=parent,
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_subspecies] {0} {1}.".format(action, obj))
    return obj


def make_variety(x, current_dict, publication_dict, taxon_dict):
    """Create or update a Taxon of rank Variety.

    Arguments

    x An instance of HbvSpecies, rank_name "Variety"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict for parent species name to Taxon instance

    Return The created or updated instance of Taxon.
    """
    try:
        parent = taxon_dict[x.species]
    except KeyError:
        logger.warn("[make_variety] Couldn't find record for subspecies "
                    "{0}, using genus {1} as parent".format(x.infra_name, x.genus))
        parent = Taxon.objects.get(name=x.genus)
    dd = dict(
        name=x.infra_name,
        rank=Taxon.RANK_VARIETY,
        current=current_dict[x.is_current],
        parent=parent,
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_variety] {0} {1}.".format(action, obj))
    return obj


def make_form(x, current_dict, publication_dict, taxon_dict):
    """Create or update a Taxon of rank Form.

    Arguments

    x An instance of HbvSpecies, rank_name "Variety"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict for parent species name to Taxon instance

    Return The created or updated instance of Taxon.
    """
    try:
        parent = taxon_dict[x.species]
    except KeyError:
        logger.warn("[make_variety] Couldn't find record for subspecies "
                    "{0}, using genus {1} as parent".format(x.infra_name, x.genus))
        parent = Taxon.objects.get(name=x.genus)
    dd = dict(
        name=x.infra_name2 or x.infra_name,
        rank=Taxon.RANK_FORMA,
        current=current_dict[x.is_current],
        parent=parent,
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_form] {0} {1}.".format(action, obj))
    return obj


def update_taxon():
    """Update Taxon from Hbv data."""
    # Domain
    logger.info("[update_taxon] Creating/updating domains...")
    domain, created = Taxon.objects.update_or_create(name_id=0, name="Eukarya", rank=Taxon.RANK_DOMAIN)

    # Kingdoms
    logger.info("[update_taxon] Creating/updating kingdoms...")
    kingdoms = [Taxon.objects.update_or_create(
        name_id=x.name_id, defaults=dict(name=x.name, rank=Taxon.RANK_KINGDOM, parent=domain))
        for x in HbvName.objects.filter(rank_name='Kingdom')]

    # Divisions, Classes, Orders, Families
    logger.info("[update_taxon] Creating/updating divisions, classes, orders, families...")
    # ORM kung-fu to get Kingdom ID:Taxon lookup dict
    KINGDOM_ID_NAME = {x['kingdom_id']: x['kingdom_name']
                       for x in HbvFamily.objects.values('kingdom_id', 'kingdom_name')}
    KINGDOM_ID_TAXA = {x[0]: Taxon.objects.get(name=x[1]) for x in KINGDOM_ID_NAME.items()}
    CURRENT = {'N': False, 'Y': True}
    PUBLICATION = {'PN': 0, 'MS': 1, '-': 2}
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            families = [make_family(x, KINGDOM_ID_TAXA, CURRENT, PUBLICATION)
                        for x in HbvFamily.objects.all()]

    # Genera
    logger.info("[update_taxon] Creating/updating genera...")
    FAM = {x.name_id: x for x in Taxon.objects.filter(rank=Taxon.RANK_FAMILY)}
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            genera = [make_genus(x, CURRENT, PUBLICATION, FAM) for x in HbvGenus.objects.all()]

    # Species
    logger.info("[update_taxon] Creating/updating species...")
    GENUS = {x.name: x for x in Taxon.objects.filter(rank=Taxon.RANK_GENUS)}
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            species = [make_species(x, CURRENT, PUBLICATION, GENUS)
                       for x in HbvSpecies.objects.filter(rank_name="Species")]

    # # # Subspecies
    # logger.info("[update_taxon] Creating/updating subspecies...")
    # SPECIES = {x.name: x for x in Taxon.objects.filter(rank=Taxon.RANK_SPECIES)}
    # with transaction.atomic():
    #     with Taxon.objects.delay_mptt_updates():
    #         subspecies = [make_subspecies(x, CURRENT, PUBLICATION, SPECIES)
    #                       for x in HbvSpecies.objects.filter(rank_name="Subspecies")]

    # # Varieties
    # logger.info("[update_taxon] Creating/updating varieties...")
    # # SUBSPECIES = {x.name: x for x in Taxon.objects.filter(rank=Taxon.RANK_SUBSPECIES)}
    # with transaction.atomic():
    #     with Taxon.objects.delay_mptt_updates():
    #         varieties = [make_variety(x, CURRENT, PUBLICATION, SPECIES)
    #                      for x in HbvSpecies.objects.filter(rank_name="Variety")]

    # # Forms
    # logger.info("[update_taxon] Creating/updating forms...")
    # with transaction.atomic():
    #     with Taxon.objects.delay_mptt_updates():
    #         forms = [make_form(x, CURRENT, PUBLICATION, SPECIES)
    #                  for x in HbvSpecies.objects.filter(rank_name="Form")]

    msg = ("[update_taxon] Updated {0} kingdoms, {1} families "
           "and their parentage, {2} genera, {3} species"
           # ", {4} subspecies, {5} varieties, {6} forms."
           ).format(
        len(kingdoms),
        len(families),
        len(genera),
        len(species),
        # len(subspecies),
        # len(varieties),
        # len(forms)
    )
    logger.info(msg)
    return msg

# WARNING 2018-03-01 11:42:44,128 [make_subspecies]
# Couldn't find record for species virdis, using genus Anigozanthos as parent
# INFO 2018-03-01 11:42:44,714 [make_subspecies] Updated [11249]
# (Subspecies) Anigozanthos SPECIES subspecies terraspectans.

# WARNING 2018-03-01 11:43:44,291 [make_subspecies] Couldn't find record for species petiolata, using genus Decaisnina
# INFO 2018-03-01 11:43:44,986 [make_subspecies] Updated [11398] (Subspecies) Decaisnina SPECIES subspecies angustata.

# WARNING 2018-03-01 11:45:19,554 [make_subspecies] Couldn't find record for species shuttleworthina,
# using genus Grevillea
# INFO 2018-03-01 11:45:20,331 [make_subspecies] Updated [15768] (Subspecies) Grevillea SPECIES subspecies canarina.

# WARNING 2018-03-01 11:49:36,794 [make_variety] Couldn't find record for subspecies A Kimberley Flora
# (K.F. Kenneally 5452), using genus Brunonia as parent
# INFO 2018-03-01 11:49:37,844 [make_variety] Updated [15247] (Variety)
# Brunonia SPECIES variety A Kimberley Flora (K.F. Kenneally 5452).
