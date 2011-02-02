from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('contest.views',
    url('$', 'index', name='index'),
)
