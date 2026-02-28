from django.contrib import admin
from .models import (
    Profile,
    Organizer,
    Category,
    State,
    Event,
    Ticket,
    Order,
    OrderItem,
    Attendee,
    ContactMessage,

)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "gender", "status", "created_at")
    list_filter = ("gender", "status")
    search_fields = ("user__username", "phone")


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ("organization_name", "verified", "joined_at")
    list_filter = ("verified",)
    search_fields = ("organization_name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "category", "date", "status")
    list_filter = ("status", "category")
    search_fields = ("title",)
    date_hierarchy = "date"


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "price", "quantity_available")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "event", "total_amount", "status", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "event",
        "payment_status",
        "tickets_qty",
        "registered_at",
    )
    list_filter = ("payment_status",)
    search_fields = ("full_name", "email")



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_resolved")
    list_filter = ("subject", "is_resolved", "created_at")
    search_fields = ("name", "email", "message")
