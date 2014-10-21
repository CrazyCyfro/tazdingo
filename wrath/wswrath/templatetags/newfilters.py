#Read https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#
#And http://vanderwijk.info/blog/adding-css-classes-formfields-in-django-templates/
'''
from django import template
register = template.Library()

@register.filter(name='addcss')
def addcss(field, css):
   return field.as_widget(attrs={"class":css})
'''
from django import template
from wswrath.models import URL, URLComparison, Rating
register = template.Library()

@register.filter(name='addcss')
def addcss(field, css):
  attrs = {}
  definition = css.split(',')

  for d in definition:
    if ':' not in d:
      attrs['class'] = d
    else:
      t, v = d.split(':')
      attrs[t] = v

  return field.as_widget(attrs=attrs)

def get_range( value ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return range(0,value,50)

def get_title(value ):
  url

@register.filter(name='distancetop')
def distancetop(x):
    # you would need to do any localization of the result here
    return 200+x/3*200

@register.filter(name='distanceleft')
def distanceleft(x):
    return 100+x%3*500