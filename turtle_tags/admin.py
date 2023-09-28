from django.contrib.admin import register
from reversion.admin import VersionAdmin

from .models import (
    Turtle,
    TagPurchaseOrder,
    TurtleTag,
)


@register(Turtle)
class TurtleAdmin(VersionAdmin):
    date_hierarchy = "created"
    list_display = ("id", "species", "sex", "source", "source_id")
    list_filter = ("species", "sex", "source")
    search_fields = ("name", "source_id")

    fields = (
        "species",
        "sex",
        "name",
        "comments",
    )
    readonly_fields = ("entered_by", "source", "source_id")

    def response_add(self, request, obj, post_url_continue=None):
        """Set the request user as the person who entered the record.
        """
        obj.entered_by = request.user
        obj.save()

        return super().response_add(request, obj, post_url_continue)


@register(TagPurchaseOrder)
class TagPurchaseOrderAdmin(VersionAdmin):
    date_hierarchy = "order_date"
    list_display = ("id", "order_number", "order_date", "date_received", "total")
    search_fields = ("order_number", "paid_by", "comments")

    fields = (
        "order_number",
        "order_date",
        "date_received",
        "tag_prefix",
        "total",
        "paid_by",
        "comments",
    )
    readonly_fields = ("source", "source_id")


@register(TurtleTag)
class TurtleTagAdmin(VersionAdmin):
    date_hierarchy = "created"
    list_display = ("id", "serial", "tag_type", "turtle", "order")
    list_filter = ("tag_type",)
    search_fields = (
        "serial", "order__order_number", "turtle__name", "custodian__name", "field_handler__name",
        "comments", "batch_number", "box_number",
    )

    fields = (
        "serial",
        "tag_type",
        "turtle",
        "order",
        "custodian",
        "field_handler",
        "side",
        "return_date",
        "return_condition",
        "comments",
        "batch_number",
        "box_number",
    )
    readonly_fields = ("entered_by", "source", "source_id")
