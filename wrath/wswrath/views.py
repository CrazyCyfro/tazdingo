from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from wswrath.models import UserProfile, URL, URLComparison, Rating
from wswrath.forms import UserForm, UserProfileForm, URLForm, URLComparisonForm, URLSearchForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required    
from django.http import HttpResponseRedirect, HttpResponse

import urllib2
from bs4 import BeautifulSoup
import string
import threading
import math
import random
import json

def removePunct(temp):
  cleaned = ""
  for char in temp:
    if char in string.digits or char in string.letters or char == ' ':
      cleaned += char
      
  return cleaned

def compareToAll(url):
  page_list = URL.objects.all()
  for page in page_list:
    if url != page:
      percentage = compare(url.url,page.url)
      if url.url < page.url:
        comparison = URLComparison(url1 = url, url2 = page, percent = percentage)
      else:
        comparison = URLComparison(url1 = page, url2 = url, percent = percentage)
      comparison.save()

def clean(dictionary):
  commonwords = ['the','be','to','of','and','in','that','have','it','for','not','on','with','he','as','you','do','at','this','but','his','by','from','they','we','say','her','she','or','an','will','my','one','all','would','there','their','what','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
  
  newdict = {}
  for word in dictionary:
    if word not in commonwords:
      if word not in newdict:
        newdict[word] = 1
      else:
        newdict[word] += 1

  return newdict

def total(dictionary):
  count = 0
  for i in dictionary:
    count += dictionary[i]
  
  return count

def title(url):
  soup = BeautifulSoup(urllib2.urlopen(url).read())
  
  return soup.title.string

def urldict(url):
  soup = BeautifulSoup(urllib2.urlopen(url).read())

  [s.extract() for s in soup.find_all(['script','style','span'])]
  text = soup.find_all(['title','h1','h2','h3','h4','h5','p','a'])

  info = ""
  for i in text:
    readable = i.get_text()
    readable = readable.lower()
    if readable.endswith(" ") != True:
      readable += " "
    info += readable

    wordcount = {}
    for word in info.split():
      cleanedWord = removePunct(word)
      if cleanedWord != "":
        if cleanedWord not in wordcount:
          wordcount[cleanedWord] = 1
        else:
          wordcount[cleanedWord] += 1
  
  return wordcount

def compare(url1, url2):
  wordcount1 = clean(urldict(url1))
  wordcount2 = clean(urldict(url2))

  finalcount = {}

  for key in wordcount1:
    if key in wordcount2:
      finalcount[key] = min(wordcount1[key], wordcount2[key])

  percent = (float(total(finalcount))/min(total(wordcount1),total(wordcount2)))*100
  
  return percent

def ratingcomparator(link1, link2):
  if (link1.rating != link2.rating):
    return link1.rating >= link2.rating
  return link1.percent >= link2.percent

def load_index():
  page_list = URL.objects.all()
  context_dict = {'pages': page_list}
  return context_dict

def index(request):
  context = RequestContext(request)
  page_list = URL.objects.all()
  pages = []
  context_dict = {}
  
  try:
    profile = UserProfile.objects.get(user = request.user.id)
    recent_viewed = profile.recent
    context_dict['recent'] = recent_viewed.all()
  except ObjectDoesNotExist:
    print "Unauthenticated User / Superuser"
  
  i = 0
  while i < min(5, len(page_list)):
    rand = random.randint(0,len(page_list) - 1)
    if page_list[rand] not in pages:
      pages.append(page_list[rand])
      i += 1
  
  context_dict['pages'] = pages  
  
  if request.method == 'POST':
    form = URLForm(request.POST)
    if form.is_valid():
      urlsave = form.save(commit = False)
      url = request.POST['url']
      uneditedtitle = title(url)
      editedtitle = ""
      for char in uneditedtitle:
        if len(editedtitle) < 25:
          editedtitle += char
        else:
          editedtitle += "..."
          break
      
      urlsave.title = uneditedtitle
      urlsave.shorttitle = editedtitle
      
      temp = ""
      for char in urlsave.title:
        if char in string.letters or char in string.digits or char == ' ':
          temp += char
      
      urlsave.cleaned = temp
      urlsave.urltitle = temp.replace(' ','_')
      urlsave.save()
      
      form.save_m2m()
      
      context_dict['form'] = form
      
      t = threading.Thread(target = compareToAll,args=[urlsave])
      t.setDaemon(False)
      t.start()
      
      return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
      
  else:
    form = URLForm()
    context_dict['form'] = form
    
  return render_to_response('wswrath/index.html', context_dict, context)
  
def register(request):
  context = RequestContext(request)
  registered = False

  if request.method == 'POST':
    user_form = UserForm(data=request.POST)
    profile_form = UserProfileForm(data=request.POST)
    
    if user_form.is_valid() and profile_form.is_valid():
      user = user_form.save()
      user.set_password(user.password)
      user.save()
            
      profile = profile_form.save(commit=False)
      profile.user = user
      profile.save()
      registered = True

    else:
      print user_form.errors, profile_form.errors
  
  else:
    user_form = UserForm()
    profile_form = UserProfileForm()
    
  return render_to_response('wswrath/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}, context)


def user_login(request):
  context = RequestContext(request)

  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    
    if user:
      if user.is_active:
        login(request, user)
        return HttpResponseRedirect('/wswrath/')
      else:
        return HttpResponse("Your Wrath account is disabled.")

    else:
      print "Invalid login details: {0}, {1}".format(username, password)
      return HttpResponse("Invalid login details supplied.")

  else:
    return render_to_response('wswrath/login.html', {}, context)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
  logout(request)
  return HttpResponseRedirect('/wswrath/')

@login_required
def compareURL(request):
  context = RequestContext(request)
  context_dict = {}
  
  if request.method == 'POST':
    form = URLComparisonForm(request.POST)
    if form.is_valid():
      
      context_dict['form'] = form

      url1 = request.POST['url1']
      url2 = request.POST['url2']
      context_dict['url1'] = url1
      context_dict['url2'] = url2
      
      percent = compare(url1,url2)
      
      context_dict['percent'] = percent

      return render_to_response('wswrath/comparison.html', context_dict, context)
    
    else:
      print form.errors
      
      form = URLComparisonForm()
      context_dict = {'form':form}
      
      return render_to_response('wswrath/compare.html', context_dict, context)

  else:
    form = URLComparisonForm()
    context_dict = {'form':form}
    
    return render_to_response('wswrath/compare.html', context_dict, context)

@login_required
def page(request, page_title_url):
  context = RequestContext(request)
  context_dict = {}
  page_title = page_title_url.replace('_', ' ')
  page = URL.objects.get(cleaned = page_title)
  context_dict['page'] = page

  comparisons = {}
  nametourl = {}
  rating = {}
  comparison_list = URLComparison.objects.all()

  for comparison in comparison_list:
    if (comparison.url1 == page):
      comparisons[comparison.url2.title] = comparison.percent
      nametourl[comparison.url2.title] = comparison.url2.urltitle
      rating[comparison.url2.title] = comparison.rating
    elif (comparison.url2 == page):
      comparisons[comparison.url1.title] = comparison.percent
      nametourl[comparison.url1.title] = comparison.url1.urltitle
      rating[comparison.url1.title] = comparison.rating
  
  topcomparisonspercent = []
  topcomparisonsrating = []

  for i in range(min(5, len(comparisons))):
    currentmaxpercent = 0.0
    currentmaxname = ""
    for name in comparisons:
      if comparisons[name] > currentmaxpercent and (name, comparisons[name], rating[name], nametourl[name]) not in topcomparisonspercent:
        currentmaxpercent = comparisons[name]
        currentmaxname = name
    
    topcomparisonspercent.append((currentmaxname, currentmaxpercent, rating[currentmaxname], nametourl[currentmaxname]))
  
  for i in range(min(5, len(rating))):
    currentmaxrating = -1000000
    currentmaxname = ""
    for name in rating:
      if rating[name] > currentmaxrating and (name, comparisons[name], rating[name], nametourl[name]) not in topcomparisonsrating:
        currentmaxrating = rating[name]
        currentmaxname = name
    
    topcomparisonsrating.append((currentmaxname, comparisons[currentmaxname], currentmaxrating, nametourl[currentmaxname]))

  context_dict['comparisonspercent'] = topcomparisonspercent
  context_dict['comparisonsrating'] = topcomparisonsrating
  
  try:
    profile = UserProfile.objects.get(user = request.user.id)
    if profile.recent.count() > 4:
      outdated = profile.recent.all()[0]
      profile.recent.remove(outdated)
        
    profile.recent.add(page)
    profile.save()
  except ObjectDoesNotExist:
    print "Unauthenticated User / Superuser"
  
  return render_to_response('wswrath/page.html', context_dict, context)

@login_required
def add_link(request):
  context = RequestContext(request)
  context_dict = {}
  
  if request.method == "POST":
    form = URLLinkForm(request.POST)
    if form.is_valid():
      form.url1 = form.cleaned_data.get('url1')
      form.url2 = form.cleaned_data.get('url2')
      
      link = form.save(commit=False)
      link.title1 = form.url1.title
      link.title2 = form.url2.title
      link.save()
      form.save_m2m()
      
      context_dict = load_index()
      
      return render_to_response('wswrath/index.html', context_dict, context)
    else:
      print form.errors
  else:
    form = URLLinkForm()
    context_dict['form'] = form
    return render_to_response('wswrath/add_link.html', context_dict, context)

@login_required
def weblink(request):
  context = RequestContext(request)
  context_dict = {}
  
  if request.method == "GET":
    link_list = URLComparison.objects.all()
    unref_link_list = []
    url_list = URL.objects.all()
    
    ref_link_list = []
    for link in link_list:
      unref_link_list.append(link)
    
    tentative_links = {}
    for url in url_list:
      tentative_links[url] = [url]
    
    for link in unref_link_list:
      if len(tentative_links[link.url1]) < 3:
        tentative_links[link.url1].append(link)
      elif ratingcomparator(link, tentative_links[link.url1][1]):
        tentative_links[link.url1][2] = tentative_links[link.url1][1]
        tentative_links[link.url1][1] = link
      elif ratingcomparator(link, tentative_links[link.url1][2]):
        tentative_links[link.url1][2] = link
      
      if len(tentative_links[link.url2]) < 3:
        tentative_links[link.url2].append(link)
      elif ratingcomparator(link, tentative_links[link.url2][1]):
        tentative_links[link.url2][2] = tentative_links[link.url2][1]
        tentative_links[link.url2][1] = link
      elif ratingcomparator(link, tentative_links[link.url2][2]):
        tentative_links[link.url2][2] = link
    
    for url in tentative_links:
      tentative_links_urltitles = []
      for tlink in tentative_links[url]:
        if tlink != tentative_links[url][0]:
          if tlink.url1 == url:
            tentative_links_urltitles.append(tlink.url2)
          elif tlink.url2 == url:
            tentative_links_urltitles.append(tlink.url1)
        else:
          tentative_links_urltitles.append(tentative_links[url][0])
          
      ref_link_list.append(tentative_links_urltitles)
    
    context_dict['links'] = ref_link_list
    context_dict['urls'] = url_list
    context_dict['urlnumplusone'] = len(url_list) + 1
    context_dict['urlnumplustwo'] = len(url_list) + 2  
    
    return render_to_response('wswrath/weblink.html', context_dict, context)
  else:
    context_dict = load_index()
    return render_to_response('wswrath/index.html', context_dict, context)

@login_required
def upvote(request, page_title_url1, page_title_url2):
  cleanedpage1 = page_title_url1.replace('_',' ')
  cleanedpage2 = page_title_url2.replace('_',' ')
  page1 = URL.objects.get(cleaned = cleanedpage1)
  page2 = URL.objects.get(cleaned = cleanedpage2)
  
  if (page1.url < page2.url):
    comparison = URLComparison.objects.get(url1 = page1, url2 = page2)
  else:
    comparison = URLComparison.objects.get(url1 = page2, url2 = page1)

  rating, created = Rating.objects.get_or_create(urllink = comparison, user = request.user)
  
  if created:
    comparison.rating += 1
    comparison.save()
    rating.updown = True
    rating.save()
  
  elif not rating.updown:
    comparison.rating += 2
    comparison.save()
    rating.updown = True
    rating.save()
    
  return page(request, page_title_url1)

@login_required
def downvote(request, page_title_url1, page_title_url2):
  cleanedpage1 = page_title_url1.replace('_',' ')
  cleanedpage2 = page_title_url2.replace('_',' ')
  page1 = URL.objects.get(cleaned = cleanedpage1)
  page2 = URL.objects.get(cleaned = cleanedpage2)
  
  if (page1.url < page2.url):
    comparison = URLComparison.objects.get(url1 = page1, url2 = page2)
  else:
    comparison = URLComparison.objects.get(url1 = page2, url2 = page1)

  rating, created = Rating.objects.get_or_create(urllink = comparison, user = request.user)
  
  if created:
    comparison.rating -= 1
    comparison.save()
    rating.updown = False
    rating.save()
  
  elif rating.updown:
    comparison.rating -= 2
    comparison.save()
    rating.updown = False
    rating.save()
    
  return page(request, page_title_url1)

