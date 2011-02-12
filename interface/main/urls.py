from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('main.views',
    url('$', 'index', name='index'),
    url('problem/(?P<problem_slug>[-\w]+)/', 'problem', name='problem'), 
)
