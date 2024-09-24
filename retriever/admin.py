from django.contrib import admin
from .models import Documents, QueryHistory


admin.site.register(Documents)



@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','query', 'color', 'checked')
    list_filter = ('query', 'color', 'checked')
    # search_fields = ('query', 'color', 'checked')
    # pass

# Register your models here.
