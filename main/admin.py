from datetime import datetime, timedelta
import logging
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.db.models.functions import TruncDay
from django.db.models import Count
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from . import models, forms

logger = logging.getLogger(__name__)


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal information",
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
        (None,{
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
        "is_active"
        )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


def make_active(self, request, queryset):
    queryset.update(active=True)
make_active.short_description = "Mark selected books as active"

def make_inactive(self, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = "Mark selected books as inactive"

class BookAdmin(admin.ModelAdmin):
    list_display = ("name","price","in_stock",)
    list_filter = ("active", "in_stock", "date_updated")
    list_editable = ("in_stock",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("tags",)
    
    actions = [make_active, make_inactive]
    
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ["slug", "name"]
    
    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}

class InvoiceMixin:
    # This mixin will be used for the invoice generation, which is 
    # only available to owners and employees
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("invoice/<int:order_id>/",self.admin_view(self.invoice_for_order),name="invoice")]
        return my_urls + urls
    
    def invoice_for_order(self, request, order_id):
        order = get_object_or_404(models.Order, pk=order_id)
        if request.GET.get("format") == "pdf":
            html_string = render_to_string("invoice.html", {"order": order})
            html = HTML(string=html_string, base_url=request.build_absolute_url())
            result = html.write_pdf()
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = "inline; filename=invoice.pdf"
            response["Content-Transfer-Encoding"] = "binary"
            
            with tempfile.NamedTemporaryFile( delete=True) as output:
                output.write(result)
                output.flush()
                output = open(output.name, "rb")
                binary_pdf = output.read()
                response.write(binary_pdf)
            return response
        return render(request, "invoice.html", {"order": order})

       
class DispatchersBookAdmin(BookAdmin):
    readonly_fields = ("description", "price", "tags", "active")
    prepopulated_fields = {}
    autocomplete_fields = ()

class BookTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_filter = ("active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    
    # def get_readonly_fields(self, request, obj=None):
    #     if request.user.is_superuser:
    #         return self.readonly_field
    #     return list(self.readonly_fields) + ["slug", "name"]
    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}
class BookImageAdmin(admin.ModelAdmin):
    list_display = ( "book_name","thumbnail_tag")
    readonly_fields = ("thumbnail",)
    search_fields = ("book__name",)
    
    # this function returns HTML for the first column defined
    # in the list_display property above
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html('<img src="%s"/>' % obj.thumbnail.url)
        return "-"
    
    # this defines the column name for the list_display 
    # that is done by the helper ``` short_description```
    thumbnail_tag.short_description = "Thumbnail Image"
    
    def book_name(self, obj):
        return obj.book.name

class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "address",
        "town")
    readonly_fields = ("user",)

class BasketLineInline(admin.TabularInline):
    model = models.BasketLine
    raw_id_fields = ("book",)
@admin.register(models.Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "count")
    list_editable = ("status",)
    list_filter = ("status",)
    inlines = (BasketLineInline,)
class OrderLineInline(admin.TabularInline):
    model = models.OrderLine
    raw_id_fields = ("book",)
    extra: 2
    # readonly_fields = ('book',)

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    list_filter = ("status", "shipping_county", "date_added")
    inlines = (OrderLineInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing information",
            {
                "fields": (
                    "billing_name",
                    "billing_address",
                    "billing_town",
                    "billing_county",
                    )
                },
            ),
        (
            "Shipping information",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address",
                    "shipping_town",
                    "shipping_county",
                    )
                },
            ),
        )
# Employees have a custom version of the order views because
# they are not allowed to change books already purchased
# without adding and removing lines
class CentralOfficeOrderLineInline(admin.TabularInline):
    model = models.OrderLine
    readonly_fields = ("book",)
class CentralOfficeOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    readonly_fields = ("user",)
    list_filter = ("status", "shipping_county", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing information",
            {
                "fields": (
                    "billing_name",
                    "billing_address",
                    "billing_town",
                    "billing_county",
                    )
                },
            ),
        (
            "Shipping information",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address",
                    "shipping_town",
                    "shipping_county",
                    )
                },
            ),
        )
# Dispatchers do not need to see the billing address in the fields
class DispatchersOrderAdmin(admin.ModelAdmin):
    list_display = ("id","shipping_name","date_added","status",)
    list_filter = ("status", "shipping_county", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address",
                    "shipping_town",
                    "shipping_county",
                    )
                },
            ),
        )
    
    # Dispatchers are only allowed to see orders that
    # are ready to be shipped
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=models.Order.PAID)

# The class below will pass to the Django Admin templates a couple
# of extra values that represent colors of headings
class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context["site_header_color"] = getattr(self, "site_header_color", None)
        context["module_caption_color"] = getattr(self, "module_caption_color", None)
        return context

# The following will add reporting views to the list of
# available urls and will list them from the index page
class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("orders_per_day/",self.admin_view(self.orders_per_day)),
            path("most_bought_books/",self.admin_view(self.most_bought_products),name="most_bought_products"),
            ]
        return my_urls + urls
    
    def orders_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)
        order_data = (
            models.Order.objects.filter(date_added__gt=starting_day).annotate(day=TruncDay("date_added"))
            .values("day").annotate(c=Count("id")))
        labels = [x["day"].strftime("%Y-%m-%d") for x in order_data]
        values = [x["c"] for x in order_data]
        context = dict(
            self.each_context(request),
            title="Orders per day",
            labels=labels,
            values=values)
        return TemplateResponse(request, "orders_per_day.html", context)
    
    def most_bought_products(self, request):
        if request.method == "POST":
            form = forms.PeriodSelectForm(request.POST)
            if form.is_valid():
                days = form.cleaned_data["period"]
                starting_day = datetime.now() - timedelta(days=days )
                data = (models.OrderLine.objects.filter(order__date_added__gt=starting_day)
                        .values("book__name")
                        .annotate(c=Count("id")))
            logger.info("most_bought_books query: %s", data.query)
            labels = [x["book__name"] for x in data]
            values = [x["c"] for x in data]
        else:
            form = forms.PeriodSelectForm()
            labels = None
            values = None
        
        context = dict(
            self.each_context(request),
            title="Most bought books",
            form=form,
            labels=labels,
            values=values,
            )
        
        return TemplateResponse(request, "most_bought_books.html", context)
    
        
    def index(self, request, extra_context=None):
        reporting_pages = [
            {
                "name": "Orders per day",
                "link": "orders_per_day/",
                },
            {
               "name": "Most bought books",
               "link": "most_bought_books/", 
            }
            ]
        if not extra_context:
            extra_context = {}
            extra_context = {"reporting_pages": reporting_pages}
            return super().index(request, extra_context)

# AdminSite, each with their own set of required permissions and colors
class OwnersAdminSite(InvoiceMixin, ReportingColoredAdminSite):
    site_header = "EBOOKSTORE owners administration"
    site_header_color = "black"
    module_caption_color = "grey"
    def has_permission(self, request):
        return (request.user.is_active and request.user.is_superuser)
class CentralOfficeAdminSite(InvoiceMixin, ReportingColoredAdminSite):
    site_header = "EBOOKSTORE central office administration"
    site_header_color = "purple"
    module_caption_color = "pink"
    def has_permission(self, request):
        return (request.user.is_active and request.user.is_employee)
class DispatchersAdminSite(ColoredAdminSite):
    site_header = "EBOOKSTORE central dispatch administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"
    def has_permission(self, request):
        return (request.user.is_active and request.user.is_dispatcher
                
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