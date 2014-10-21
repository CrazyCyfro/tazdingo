from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^register/$', views.register, name='register'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout'),
        url(r'^compare/$', views.compareURL, name='compare'),
        url(r'^pages/(?P<page_title_url>\w+)/$', views.page, name='page'),
        url(r'^pages/(?P<page_title_url1>\w+)/(?P<page_title_url2>\w+)/upvote/$', views.upvote, name='upvote'),
        url(r'^pages/(?P<page_title_url1>\w+)/(?P<page_title_url2>\w+)/downvote/$', views.downvote, name = 'downvote'),
        url(r'^weblink/$', views.weblink, name='weblink'),
)
