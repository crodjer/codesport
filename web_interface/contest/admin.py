from contest.models import Problem, TestPair
from django.contrib import admin


def mark_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
mark_public.short_description = "Mark selected stories as public"

def mark_not_public(modeladmin, request, queryset):
    queryset.update(is_public=False)
mark_not_public.short_description = "Mark selected stories as not public"

class TestPairInline(admin.TabularInline):
	model = TestPair
	extra = 5
class ProblemAdmin(admin.ModelAdmin):    
    list_display = ('title', 'summary', 'is_public', 'marks', 'marks_coefficient')
    inlines = [TestPairInline]
    actions = [mark_public, mark_not_public]
    search_fields = ['title', 'summary']

admin.site.register(Problem,ProblemAdmin)
