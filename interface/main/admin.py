from main.models import Problem, TestPair
from django.contrib import admin


def mark_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
mark_public.short_description = "Mark selected stories as public"

def mark_not_public(modeladmin, request, queryset):
    queryset.update(is_public=False)
mark_not_public.short_description = "Mark selected stories as not public"

def update_marks_factor(modeladmin, request, queryset):        
    for problem in queryset:
        problem.set_marks_factor()
update_marks_factor.short_description = "Update marks distribition factor"

class TestPairInline(admin.TabularInline):
	model = TestPair
	extra = 5
class ProblemAdmin(admin.ModelAdmin):
    fieldsets = [
		(None,  {'fields': ['title', 'slug', 'summary',
                                         'statement', 'level',
                                         'marks']}),
        ('Meta',  {'fields': ['is_public', 'marks_factor']}),
                
	]
    readonly_fields = ('marks_factor',)
    list_display = ('title', 'summary', 'is_public',
                    'marks', 'marks_factor')
    list_filter = ('is_public', 'published_on')
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TestPairInline]
    actions = [mark_public, mark_not_public, update_marks_factor]
    search_fields = ['title', 'summary']
    
    def save_model(self, request, obj, form, change): 
	instance = form.save(commit=False)
	instance.publisher = request.user
	instance.save()
	return instance

admin.site.register(Problem,ProblemAdmin)
