# -*- coding: utf-8 -*-
"""Helpers for Taxonomy module."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging

# from django.utils.timezone import is_aware, make_aware
# from pdb import set_trace
# from django.core.management import call_command
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils.encoding import force_text
from taxonomy import models as tax_models

logger = logging.getLogger(__name__)


def create_test_fixtures():
    """Create test fixtures for Taxonomy.

    This utility creates the following fixtures:

    taxonomy/fixtures/test_taxon.json

    * Once taxon with a vernacular name
    * One taxon that is a current name
    * One taxon that is a non-current name

    taxonomy/fixtures/test_crossreference.json
    * One crossreference of each type, including all involved taxa and their pylogeny.
      Thanks, django-fixture-magic!

    taxonomy/fixtures/test_community.json
    * The first 10 communities with related objects.
    """
    c0 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_MIS).last()
    c1 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_TSY).last()
    c2 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_NSY).last()
    c3 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_EXC).last()
    c4 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_CON).last()
    c5 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_FOR).last()
    c6 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_OGV).last()
    c7 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_ERR).last()
    c8 = tax_models.Crossreference.objects.filter(reason=tax_models.Crossreference.REASON_ISY).last()
    tv = tax_models.Taxon.objects.exclude(vernacular_name__isnull=True).last()

    xref_pks = " ".join([str(x.pk) for x in[c0, c1, c2, c3, c4, c5, c6, c7, c8]])
    taxon_pks = " ".join([str(x) for x in [tv.pk, ]])
    com_pks = " ".join([str(x.pk) for x in tax_models.Community.objects.all()[1:10]])

    print("./manage.py dump_object taxonomy.Crossreference {0} -k "
          "> taxonomy/fixtures/test_crossreference.json".format(xref_pks))
    print("./manage.py dump_object taxonomy.Taxon {0} -k "
          "> taxonomy/fixtures/test_taxon.json".format(taxon_pks))
    print("./manage.py dump_object taxonomy.Community {0} -k "
          "> taxonomy/fixtures/test_community.json".format(com_pks))

    # This throws an error on related objects
    # with open("taxonomy/fixtures/test_crossreference.json", 'w+') as f:
    #     call_command('dump_object', 'taxonomy.Crossreference', xref_pks, stdout=f)
    #     f.readlines()

    # with open("taxonomy/fixtures/test_taxon.json", 'w+') as f:
    #     call_command('dump_object', 'taxonomy.Taxon', taxon_pks, stdout=f)
    #     f.readlines()

    # with open("taxonomy/fixtures/test_community.json", 'w+') as f:
    #     call_command('dump_object', 'taxonomy.Community', com_pks, stdout=f)
    #     f.readlines()


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
            rank=tax_models.Taxon.RANK_DIVISION,
            parent=lowest_parent)
        division, created = tax_models.Taxon.objects.update_or_create(name_id=fam.division_nid, defaults=dd)
        lowest_parent = division
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, division))

    if fam.class_nid:
        dd = dict(
            name_id=fam.class_nid,
            name=force_text(fam.class_name),
            rank=tax_models.Taxon.RANK_CLASS,
            parent=lowest_parent)
        clazz, created = tax_models.Taxon.objects.update_or_create(name_id=fam.class_nid, defaults=dd)
        lowest_parent = clazz
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, clazz))

    if fam.order_nid:
        dd = dict(
            name=(fam.order_name),
            rank=tax_models.Taxon.RANK_ORDER,
            parent=lowest_parent)
        order, created = tax_models.Taxon.objects.update_or_create(name_id=fam.order_nid, defaults=dd)
        lowest_parent = order
        action = "Created" if created else "Updated"
        logger.info("[make_family] {0} {1}.".format(action, order))

    dd = dict(name=force_text(fam.family_name),
              rank=tax_models.Taxon.RANK_FAMILY,
              current=current_dict[fam.is_current],
              parent=lowest_parent,
              author=fam.author)
    if fam.informal is not None:
        dd['publication_status'] = publication_dict[fam.informal]
        print(dd['publication_status'])
    family, created = tax_models.Taxon.objects.update_or_create(name_id=fam.name_id, defaults=dd)
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
        rank=tax_models.Taxon.RANK_GENUS,
        current=current_dict[x.is_current],
        parent=tax_models.Taxon.objects.get(name_id=x.family_nid),
        author=x.author
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = tax_models.Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
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

    Return The created or updated instance of Taxon or None if parent id is missing.
    """
    parent_nid = tax_models.HbvParent.objects.get(name_id=x.name_id).parent_nid
    if not tax_models.Taxon.objects.filter(name_id=parent_nid).exists():
        logger.warn("[make_species] missing parent taxon with name_id {0}, re-run to fix.".format(parent_nid))
        return None

    dd = dict(
        name=force_text(x.species),
        rank=tax_models.Taxon.RANK_SPECIES,
        current=current_dict[x.is_current],
        parent_id=tax_models.Taxon.objects.get(name_id=parent_nid).pk,
        author=x.author,
        field_code=x.species_code
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = tax_models.Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
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
        rank=tax_models.Taxon.RANK_SUBSPECIES,
        current=current_dict[x.is_current],
        parent=tax_models.Taxon.objects.get(name_id=tax_models.HbvParent.objects.get(name_id=x.name_id).parent_nid),
        author=x.author,
        field_code=x.species_code
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = tax_models.Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
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
        rank=tax_models.Taxon.RANK_VARIETY,
        current=current_dict[x.is_current],
        parent=tax_models.Taxon.objects.get(name_id=tax_models.HbvParent.objects.get(name_id=x.name_id).parent_nid),
        author=x.author,
        field_code=x.species_code
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = tax_models.Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_variety] {0} {1}.".format(action, obj))
    return obj


def make_form(x, current_dict, publication_dict):
    """Create or update a Taxon of rank Form.

    Some forms have no known names between species and form.
    These keep the form name in the ``infra_name`` field.
    e.g.
    Caulerpa    brachypus   forma   parvifolia

    Others have a known subspecies/variety/subvariety name in the
    ``infra_name`` field, and keep the form name in ``infra_name2``:
    e.g.
    Caulerpa    cupressoides    var.    lycopodium  forma   elegans

    Arguments

    x An instance of HbvSpecies, rank_name "Variety"
    current_dict A lookup dict for is_current
    publication_dict A lookup dict for publication_status
    taxon_dict A lookup dict for parent species name to Taxon instance

    Return The created or updated instance of Taxon.
    """
    dd = dict(
        name=force_text(x.infra_name) if force_text(
            x.infra_rank) == 'forma' else force_text(x.infra_name2),
        rank=tax_models.Taxon.RANK_FORMA,
        current=current_dict[x.is_current],
        parent=tax_models.Taxon.objects.get(name_id=tax_models.HbvParent.objects.get(name_id=x.name_id).parent_nid),
        author=x.author,
        field_code=x.species_code
    )
    if x.informal is not None:
        dd['publication_status'] = publication_dict[x.informal]

    obj, created = tax_models.Taxon.objects.update_or_create(name_id=x.name_id, defaults=dd)
    action = "Created" if created else "Updated"

    logger.info("[make_form] {0} {1}.".format(action, obj))
    return obj


def make_vernacular(hbv_vern_obj, lang_dict):
    """Create or update Vernacular."""
    t = tax_models.Taxon.objects.get(name_id=hbv_vern_obj.name_id)
    dd = dict(
        ogc_fid=hbv_vern_obj.ogc_fid,
        taxon=t,
        name=hbv_vern_obj.vernacular,
        language=lang_dict[hbv_vern_obj.language] if hbv_vern_obj.language else None,
        preferred=True if (hbv_vern_obj.lang_pref and hbv_vern_obj.lang_pref == "Y") else False
    )
    obj, created = tax_models.Vernacular.objects.update_or_create(ogc_fid=hbv_vern_obj.ogc_fid, defaults=dd)
    action = "Created" if created else "Updated"
    t.save()
    logger.info("[make_vernacular] {0} {1}.".format(action, obj))
    return obj


def make_crossreference(hbv_xref_obj, reason_dict):
    """Create or update Crossreference."""
    try:
        if hbv_xref_obj.old_name_id:
            pre = tax_models.Taxon.objects.get(name_id=hbv_xref_obj.old_name_id)
        else:
            pre = None

        if hbv_xref_obj.new_name_id:
            suc = tax_models.Taxon.objects.get(name_id=hbv_xref_obj.new_name_id)
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
        obj, created = tax_models.Crossreference.objects.update_or_create(xref_id=hbv_xref_obj.xref_id, defaults=dd)
        action = "Created" if created else "Updated"
        # pre.save()
        # suc.save()
        logger.info("[make_crossreference] {0} {1}.".format(action, obj))
        return obj
    except:
        logger.warn("[make_crossreference] Failed to create Crossreference "
                    "for xref_id {0}, skipping.".format(hbv_xref_obj.xref_id))
        return None


# def make_paraphyletic_group_m2m(x):
#     """Create a paraphylectic group membership from a dict."""
#     return


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
    domain, created = tax_models.Taxon.objects.update_or_create(
        name_id=0, defaults=dict(name="Eukarya", rank=tax_models.Taxon.RANK_DOMAIN, current=True, parent=None))
    # comms, created = Taxon.objects.update_or_create(
    #     name_id=1000000, defaults=dict(name="Communities", rank=Taxon.RANK_DOMAIN, current=True, parent=thing))

    # Kingdoms
    logger.info("[update_taxon] Creating/updating kingdoms...")
    kingdoms = [tax_models.Taxon.objects.update_or_create(
        name_id=x.name_id, defaults=dict(name=x.name, rank=tax_models.Taxon.RANK_KINGDOM, current=True, parent=domain))
        for x in tax_models.HbvName.objects.filter(rank_name='Kingdom')]

    # Divisions, Classes, Orders, Families
    logger.info("[update_taxon] Creating/updating divisions, classes, orders, families...")
    # ORM kung-fu to get Kingdom ID:Taxon lookup dict
    KINGDOM_ID_NAME = {x['kingdom_id']: x['kingdom_name']
                       for x in tax_models.HbvFamily.objects.values('kingdom_id', 'kingdom_name')}
    KINGDOM_ID_TAXA = {x[0]: tax_models.Taxon.objects.get(name=x[1]) for x in KINGDOM_ID_NAME.items()}
    CUR = {'N': False, 'Y': True}
    PUB = {'PN': 0, 'MS': 1, '-': 2}
    with transaction.atomic():
        with tax_models.Taxon.objects.delay_mptt_updates():
            families = [make_family(x, KINGDOM_ID_TAXA, CUR, PUB) for x in tax_models.HbvFamily.objects.all()]

    # Genera
    logger.info("[update_taxon] Creating/updating genera...")
    with transaction.atomic():
        with tax_models.Taxon.objects.delay_mptt_updates():
            genera = [make_genus(x, CUR, PUB) for x in tax_models.HbvGenus.objects.all()]

    # Species
    logger.info("[update_taxon] Creating/updating species...")
    with transaction.atomic():
        with tax_models.Taxon.objects.delay_mptt_updates():
            species = [make_species(x, CUR, PUB) for x in tax_models.HbvSpecies.objects.filter(rank_name="Species")]

    # Subspecies
    logger.info("[update_taxon] Creating/updating subspecies...")
    with transaction.atomic():
        with tax_models.Taxon.objects.delay_mptt_updates():
            subspecies = [make_subspecies(x, CUR, PUB)
                          for x in tax_models.HbvSpecies.objects.filter(rank_name="Subspecies")]

    # Varieties
    logger.info("[update_taxon] Creating/updating varieties...")
    with transaction.atomic():
        with tax_models.Taxon.objects.delay_mptt_updates():
            varieties = [make_variety(x, CUR, PUB) for x in tax_models.HbvSpecies.objects.filter(rank_name="Variety")]

    # Forms
    logger.info("[update_taxon] Creating/updating forms...")
    with transaction.atomic():
        with tax_models.Taxon.objects.delay_mptt_updates():
            forms = [make_form(x, CUR, PUB) for x in tax_models.HbvSpecies.objects.filter(rank_name="Form")]

    # Vernaculars
    logger.info("[update_taxon] Updating Vernacular Names...")
    LANG = {"ENGLISH": 0, "INDIGENOUS": 1}
    vernaculars = [make_vernacular(x, LANG) for x in tax_models.HbvVernacular.objects.all()]
    logger.info("[update_taxon] Updated {0} Vernacular Names.".format(tax_models.Vernacular.objects.count()))

    # Crossreferences
    logger.info("[update_taxon] Updating Crossreferences...")
    REASONS = {"MIS": 0, "TSY": 1, "NSY": 2, "EXC": 3, "CON": 4, "FOR": 5, "OGV": 6, "ERR": 7, "ISY": 8}
    crossreferences = [make_crossreference(x, REASONS) for x in tax_models.HbvXref.objects.filter(active="Y")]
    logger.info("[update_taxon] Updated {0} Crossreferences.".format(tax_models.Crossreference.objects.count()))

    # Paraphyletic Groups
    logger.info("[update_taxon] Updating Paraphyletic Groups...")
    # A dict name_id:pk of Taxon. No need to fetch the actual objects.
    tt = {x["name_id"]: x["pk"] for x in tax_models.Taxon.objects.all().values('pk', 'name_id')}

    # Update the M2M end "taxon_set" of each paraphyletic group (HbvSupra) with many Taxon pks:
    [s.taxon_set.set(
        [tt[x["name_id"]]
         for x in tax_models.HbvGroup.objects.filter(class_id=s.supra_code).values('name_id', 'name')
         if x["name"] in tt]
    ) for s in tax_models.HbvSupra.objects.all()]

    logger.info(
        "[update_taxon] Updated {0} Taxon memberships of {1} Paraphyletic Groups.".format(
            tax_models.HbvGroup.objects.count(),
            tax_models.HbvSupra.objects.count()
        )
    )

    # Rebuild MPTT tree
    logger.info("[update_taxon] Rebuilding taxonomic tree - this could take a while.")
    tax_models.Taxon.objects.rebuild()
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
