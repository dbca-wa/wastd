# -*- coding: utf-8 -*-
from ajax_select import register, LookupChannel
from .models import Taxon


@register('taxon')
class TaxonLookup(LookupChannel):

    model = Taxon

    def get_query(self, q, request):
        return self.model.objects.filter(taxonomic_name__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item.taxonomic_name
