"""Helpers for Taxonomy module."""
from __future__ import division, print_function, unicode_literals, absolute_import
import logging
from django.utils.dateparse import parse_datetime
# from django.utils.timezone import is_aware, make_aware
# from pdb import set_trace
from django.db import transaction
from django.utils.encoding import force_text
from taxonomy.models import (
    Taxon, Vernacular, Crossreference,
    HbvName, HbvFamily, HbvGenus, HbvSpecies,
    HbvParent, HbvVernacular, HbvXref)

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
            name=force_text(fam.division_name),
            rank=Taxon.RANK_DIVISION,
            parent=lowest_parent)
        division, created = Taxon.objects.update_or_create(name_id=fam.division_nid, defaults=dd)
        lowest_parent = division
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, division))

    if fam.class_nid:
        dd = dict(
            name_id=fam.class_nid,
            name=force_text(fam.class_name),
            rank=Taxon.RANK_CLASS,
            parent=lowest_parent)
        clazz, created = Taxon.objects.update_or_create(name_id=fam.class_nid, defaults=dd)
        lowest_parent = clazz
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, clazz))

    if fam.order_nid:
        dd = dict(
            name=(fam.order_name),
            rank=Taxon.RANK_ORDER,
            parent=lowest_parent)
        order, created = Taxon.objects.update_or_create(name_id=fam.order_nid, defaults=dd)
        lowest_parent = order
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, order))

    dd = dict(name=force_text(fam.family_name),
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


def make_genus(x, current_dict, publication_dict):
    """Create or update a Taxon of rank Genus.

    Arguments

    x An instance of HbvGenus
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict of parent Family name_id to Taxon instance

    Return The created or updated instance of Taxon.
    """
    dd = dict(
        name=force_text(x.genus),
        rank=Taxon.RANK_GENUS,
        current=current_dict[x.is_current],
        parent=Taxon.objects.get(name_id=x.family_nid),
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


def make_species(x, current_dict, publication_dict):
    """Create or update a Taxon of rank Species.

    Arguments

    x An instance of HbvSpecies, rank_name "Species"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict of parent Genus name to Taxon instance

    Return The created or updated instance of Taxon.
    """
    dd = dict(
        name=force_text(x.species),
        rank=Taxon.RANK_SPECIES,
        current=current_dict[x.is_current],
        parent=Taxon.objects.get(name_id=HbvParent.objects.get(name_id=x.name_id).parent_nid),
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_species] {0} {1}.".format(action, obj))
    return obj


def make_subspecies(x, current_dict, publication_dict):
    """Create or update a Taxon of rank Subspecies.

    Arguments

    x An instance of HbvSpecies, rank_name "Subspecies"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status

    Return The created or updated instance of Taxon.
    """
    dd = dict(
        name=force_text(x.infra_name),
        rank=Taxon.RANK_SUBSPECIES,
        current=current_dict[x.is_current],
        parent=Taxon.objects.get(name_id=HbvParent.objects.get(name_id=x.name_id).parent_nid),
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_subspecies] {0} {1}.".format(action, obj))
    return obj


def make_variety(x, current_dict, publication_dict):
    """Create or update a Taxon of rank Variety.

    Arguments

    x An instance of HbvSpecies, rank_name "Variety"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict for parent species name to Taxon instance

    Return The created or updated instance of Taxon.
    """
    dd = dict(
        name=force_text(x.infra_name),
        rank=Taxon.RANK_VARIETY,
        current=current_dict[x.is_current],
        parent=Taxon.objects.get(name_id=HbvParent.objects.get(name_id=x.name_id).parent_nid),
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_variety] {0} {1}.".format(action, obj))
    return obj


def make_form(x, current_dict, publication_dict):
    """Create or update a Taxon of rank Form.

    Arguments

    x An instance of HbvSpecies, rank_name "Variety"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict for parent species name to Taxon instance

    Return The created or updated instance of Taxon.
    """
    dd = dict(
        name=force_text(x.infra_name2) or force_text(x.infra_name),
        rank=Taxon.RANK_FORMA,
        current=current_dict[x.is_current],
        parent=Taxon.objects.get(name_id=HbvParent.objects.get(name_id=x.name_id).parent_nid),
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_form] {0} {1}.".format(action, obj))
    return obj


def make_vernacular(hbv_vern_obj, lang_dict):
    """Create or update Vernacular."""
    t = Taxon.objects.get(name_id=hbv_vern_obj.name_id)
    dd = dict(
        ogc_fid=hbv_vern_obj.ogc_fid,
        taxon=t,
        name=hbv_vern_obj.vernacular,
        language=lang_dict[hbv_vern_obj.language],
        preferred=True if (hbv_vern_obj.lang_pref and hbv_vern_obj.lang_pref == "Y") else False
    )
    obj, created = Vernacular.objects.update_or_create(ogc_fid=hbv_vern_obj.ogc_fid, defaults=dd)
    action = "Created" if created else "Updated"
    t.save()
    logger.info("[make_vernacular] {0} {1}.".format(action, obj))
    return obj


def make_crossreference(hbv_xref_obj, reason_dict):
    """Create or update Crossreference."""
    try:
        if hbv_xref_obj.old_name_id:
            pre = Taxon.objects.get(name_id=hbv_xref_obj.old_name_id)
        else:
            pre = None

        if hbv_xref_obj.new_name_id:
            suc = Taxon.objects.get(name_id=hbv_xref_obj.new_name_id)
        else:
            suc = None

        if hbv_xref_obj.authorised_on:
            auth_on = parse_datetime("{0}T00:00:00+00:00".format(hbv_xref_obj.authorised_on))
            # auth_on = x if is_aware(x) else make_aware(x)
        else:
            auth_on = None

        dd = dict(
            xref_id=hbv_xref_obj.xref_id,
            predecessor=pre,
            successor=suc,
            reason=reason_dict[hbv_xref_obj.xref_type],
            authorised_by=hbv_xref_obj.authorised_by,
            authorised_on=auth_on,
            comments=hbv_xref_obj.comments
        )
        obj, created = Crossreference.objects.update_or_create(xref_id=hbv_xref_obj.xref_id, defaults=dd)
        action = "Created" if created else "Updated"
        # pre.save()
        # suc.save()
        logger.info("[make_crossreference] {0} {1}.".format(action, obj))
        return obj
    except:
        logger.warn("[make_crossreference] Failed to create Crossreference "
                    "for xref_id {0}, skipping.".format(hbv_xref_obj.xref_id))
        return None


def update_taxon():
    """Update Taxon from local copy of WACensus data.

    See also
    http://django-mptt.readthedocs.io/en/latest/mptt.managers.html#mptt.managers.TreeManager.disable_mptt_updates

    """
    # Thing
    # logger.info("[update_taxon] Creating/updating thing...")
    # thing, created = Taxon.objects.update_or_create(
    #     name_id=-1, defaults=dict(name="Thing", current=True, rank=Taxon.RANK_THING))

    # Domain
    logger.info("[update_taxon] Creating/updating domains...")
    domain, created = Taxon.objects.update_or_create(
        name_id=0, defaults=dict(name="Eukarya", rank=Taxon.RANK_DOMAIN, current=True, parent=None))
    # comms, created = Taxon.objects.update_or_create(
    #     name_id=1000000, defaults=dict(name="Communities", rank=Taxon.RANK_DOMAIN, current=True, parent=thing))

    # Kingdoms
    logger.info("[update_taxon] Creating/updating kingdoms...")
    kingdoms = [Taxon.objects.update_or_create(
        name_id=x.name_id, defaults=dict(name=x.name, rank=Taxon.RANK_KINGDOM, current=True, parent=domain))
        for x in HbvName.objects.filter(rank_name='Kingdom')]

    # Divisions, Classes, Orders, Families
    logger.info("[update_taxon] Creating/updating divisions, classes, orders, families...")
    # ORM kung-fu to get Kingdom ID:Taxon lookup dict
    KINGDOM_ID_NAME = {x['kingdom_id']: x['kingdom_name']
                       for x in HbvFamily.objects.values('kingdom_id', 'kingdom_name')}
    KINGDOM_ID_TAXA = {x[0]: Taxon.objects.get(name=x[1]) for x in KINGDOM_ID_NAME.items()}
    CUR = {'N': False, 'Y': True}
    PUB = {'PN': 0, 'MS': 1, '-': 2}
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            families = [make_family(x, KINGDOM_ID_TAXA, CUR, PUB) for x in HbvFamily.objects.all()]

    # Genera
    logger.info("[update_taxon] Creating/updating genera...")
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            genera = [make_genus(x, CUR, PUB) for x in HbvGenus.objects.all()]

    # Species
    logger.info("[update_taxon] Creating/updating species...")
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            species = [make_species(x, CUR, PUB) for x in HbvSpecies.objects.filter(rank_name="Species")]

    # Subspecies
    logger.info("[update_taxon] Creating/updating subspecies...")
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            subspecies = [make_subspecies(x, CUR, PUB) for x in HbvSpecies.objects.filter(rank_name="Subspecies")]

    # Varieties
    logger.info("[update_taxon] Creating/updating varieties...")
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            varieties = [make_variety(x, CUR, PUB) for x in HbvSpecies.objects.filter(rank_name="Variety")]

    # Forms
    logger.info("[update_taxon] Creating/updating forms...")
    with transaction.atomic():
        with Taxon.objects.delay_mptt_updates():
            forms = [make_form(x, CUR, PUB) for x in HbvSpecies.objects.filter(rank_name="Form")]

    # Vernaculars
    logger.info("[update_taxon] Updating Vernacular Names...")
    LANG = {"ENGLISH": 0, "INDIGENOUS": 1}
    vernaculars = [make_vernacular(x, LANG) for x in HbvVernacular.objects.all()]
    logger.info("[update_taxon] Updated {0} Vernacular Names.".format(Vernacular.objects.count()))

    # Crossreferences
    logger.info("[update_taxon] Updating Crossreferences...")
    REASONS = {"MIS": 0, "TSY": 1, "NSY": 2, "EXC": 3, "CON": 4, "FOR": 5, "OGV": 6, "ERR": 7, "ISY": 8}
    crossreferences = [make_crossreference(x, REASONS) for x in HbvXref.objects.filter(active="Y")]
    logger.info("[update_taxon] Updated {0} Crossreferences.".format(Crossreference.objects.count()))

    # Rebuild MPTT tree
    logger.info("[update_taxon] Rebuilding taxonomic tree - this could take a while.")
    Taxon.objects.rebuild()
    logger.info("[update_taxon] Taxonomic tree rebuilt.")

    # Say bye
    msg = ("[update_taxon] Updated {0} kingdoms, {1} families "
           "and their parentage, {2} genera, {3} species"
           ", {4} subspecies, {5} varieties, {6} forms,"
           " {7} vernaculars and {8} crossreferences."
           ).format(
        len(kingdoms),
        len(families),
        len(genera),
        len(species),
        len(subspecies),
        len(varieties),
        len(forms),
        len(vernaculars),
        len(crossreferences))
    logger.info(msg)
    return msg
