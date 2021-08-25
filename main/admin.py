from datetime import datetime, timedelta
import logging
from django.contrib import admin
from django.contrib.auth.admin import (UserAdmin as DjangoUserAdmin)
from django.utils.html import format_html
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum
from django.urls import path
from django.template.response import TemplateResponse
from . import models


logger = logging.getLogger(__name__)

class BookAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "in_stock", "price")
    list_filter = ("active", "in_stock", "date_updated")
    list_editable = ("in_stock",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("tags",)
    # slug is an important field for our site, it is used in
    # all the Book URLs. We want to limit the ability to
    # # change this only to the owners of the company.
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ["slug", "name"]
    # This is required for get_readonly_fields to work
    
    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}
        
class DispatchersBookAdmin(BookAdmin):
    readonly_fields = ("description", "price", "tags", "active")
    prepopulated_fields = {}
    autocomplete_fields = ()

class BookTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_filter = ("active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    
    # tag slugs also appear in urls, therefore it is a
    # property only owners can change
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_field
        return list(self.readonly_fields) + ["slug", "name"]
    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}
class BookImageAdmin(admin.ModelAdmin):
    list_display = ("thumbnail_tag", "book_name")
    readonly_fields = ("thumbnail",)
    search_fields = ("book_name",)
    # this function returns HTML for the first column defined
    # in the list_display property above
    
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="%s"/>' % obj.thumbnail.url
                )
        return "-"
    
    # this defines the column name for the list_display
    thumbnail_tag.short_description = "Thumbnail"
    
    def book_name(self, obj):
        return obj.book.name
class UserAdmin(DjangoUserAdmin):
    # User model has a lot of fields, which is why we are
    # reorganizing them for readability
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name")},
            ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    )
                },
            ),
        (
            "Important dates",
            
            {"fields": ("last_login", "date_joined")},
            ),
        )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
                },
            ),
        )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "address1",
        "address2",
        "city",
        "country",
        )
    readonly_fields = ("user",)

class BasketLineInline(admin.TabularInline):
    model = models.BasketLine
    raw_id_fields = ("book",)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "count")
    list_editable = ("status",)
    list_filter = ("status",)
    inlines = (BasketLineInline,)
class OrderLineInline(admin.TabularInline):
    model = models.OrderLine
    raw_id_fields = ("Book",)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (OrderLineInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_zip_code",
                    "billing_city",
                    "billing_country",
                    )
                },
            ),
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zip_code",
                    "shipping_city",
                    "shipping_country",
                    )
                },
            ),
        )
# Employees need a custom version of the order views because
# they are not allowed to change Books already purchased
# without adding and removing lines
class CentralOfficeOrderLineInline(admin.TabularInline):
    model = models.OrderLine
    readonly_fields = ("Book",)
class CentralOfficeOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    readonly_fields = ("user",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_zip_code",
                    "billing_city",
                    "billing_country",
                    )
                },
            ),
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zip_code",
                    "shipping_city",
                    "shipping_country",
                    )
                },
            ),
        )
# Dispatchers do not need to see the billing address in the fields
class DispatchersOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shipping_name",
        "date_added",
        "status",
        )
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zip_code",
                    "shipping_city",
                    "shipping_country",
                    )
                },
            ),
        )
    # Dispatchers are only allowed to see orders that
    # # are ready to be shipped
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=models.Order.PAID)

# The class below will pass to the Django Admin templates a couple
# of extra values that represent colors of headings
class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context["site_header_color"] = getattr(
            self, "site_header_color", None
            )
        context["module_caption_color"] = getattr(
            self, "module_caption_color", None)
        return context

# The following will add reporting views to the list of
# available urls and will list them from the index page
class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "orders_per_day/",
                self.admin_view(self.orders_per_day),
                )
            ]
        return my_urls + urls
    
    def orders_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)
        order_data = (
            models.Order.objects.filter(
                date_added__gt=starting_day
                )
            .annotate(
                day=TruncDay("date_added")
                )
            .values("day")
            .annotate(c=Count("id"))
            )
        labels = [
            x["day"].strftime("%Y-%m-%d") for x in order_data
            ]
        values = [x["c"] for x in order_data]
        context = dict(
            self.each_context(request),
            title="Orders per day",
            labels=labels,
            values=values,
            )
        return TemplateResponse(
            request, "orders_per_day.html", context
            )
        
    def index(self, request, extra_context=None):
        reporting_pages = [
            {
                "name": "Orders per day",
                "link": "orders_per_day/",
                }
            ]
        if not extra_context:
            extra_context = {}
            extra_context = {"reporting_pages": reporting_pages}
            return super().index(request, extra_context)

# Finally we define 3 instances of AdminSite, each with their own
# set of required permissions and colors
class OwnersAdminSite(ReportingColoredAdminSite):
    site_header = "BookTime owners administration"
    site_header_color = "black"
    module_caption_color = "grey"
    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_superuser
            )
class CentralOfficeAdminSite(ReportingColoredAdminSite):
    site_header = "BookTime central office administration"
    site_header_color = "purple"
    module_caption_color = "pink"
    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_employee
            )
class DispatchersAdminSite(ColoredAdminSite):
    site_header = "BookTime central dispatch administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"
    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_dispatcher
            )
main_admin = OwnersAdminSite()
main_admin.register(models.Book, BookAdmin)
main_admin.register(models.BookTag, BookTagAdmin)
main_admin.register(models.BookImage, BookImageAdmin)
main_admin.register(models.User, UserAdmin)
main_admin.register(models.Address, AddressAdmin)
main_admin.register(models.Basket, BasketAdmin)
main_admin.register(models.Order, OrderAdmin)
central_office_admin = CentralOfficeAdminSite("central-office-admin")
central_office_admin.register(models.Book, BookAdmin)
central_office_admin.register(models.BookTag,BookTagAdmin)
central_office_admin.register(models.BookImage, BookImageAdmin)
central_office_admin.register(models.Address, AddressAdmin)
central_office_admin.register(models.Order, CentralOfficeOrderAdmin)
dispatchers_admin = DispatchersAdminSite("dispatchers-admin")
dispatchers_admin.register(models.Book, DispatchersBookAdmin)
dispatchers_admin.register(models.BookTag, BookTagAdmin)
dispatchers_admin.register(models.Order, DispatchersOrderAdmin)