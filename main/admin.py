from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User, Book, BookImage, BookTag
from django.utils.html import format_html


@admin.register(User)
class AdminUser(UserAdmin):
    '''Refactored django admin configuration to match up custom User model.'''
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Permissions", {"fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )},
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        )
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        },
        )
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'in_stock', 'price')
    list_filter = ('active', 'in_stock', 'date_updated')
    list_editable = ('in_stock', )
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Book, BookAdmin)


class BookTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    # autocomplete_fields = ('tags',)


admin.site.register(BookTag, BookTagAdmin)


class BookImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag', 'book_name')
    readonly_fields = ('thumbnail',)
    # search_fields = ('book__name',)

    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html('<img src="%s"/>' % obj.thumbnail.url)
        return "-"
    thumbnail_tag.short_description = "Thumbnail"

    def book_name(self, obj):
        return obj.book.name


admin.site.register(BookImage, BookImageAdmin)
