from django import forms
from wswrath.models import User, UserProfile, URLComparison, URL, CustomComparison
from haystack.forms import SearchForm

class UserForm(forms.ModelForm):
  password = forms.CharField(widget=forms.PasswordInput())

  class Meta:
    model = User
    fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
  class Meta:
    model = UserProfile
    fields = ('website',)

class URLForm(forms.ModelForm):
  url = forms.URLField(max_length=200, help_text="Enter your URL here")
  
  class Meta:
    model = URL
    fields = ('url',)
      
class URLComparisonForm(forms.ModelForm):
  url1 = forms.URLField(max_length=200, help_text="Enter your first URL to compare")
  url2 = forms.URLField(max_length=200, help_text="Enter your second URL to compare")
   
  class Meta:
      model = CustomComparison
      fields = ('url1', 'url2',)

class URLSearchForm(SearchForm):
  def no_query_found(self):
    return self.searchqueryset.all()
  
  def search(self):
    sqs = super(URLSearchForm,self).search()
    
    if not self.is_valid():
      return self.no_query_found
    
    sqs = sqs.order_by(title)
    
    return sqs