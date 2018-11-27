# GovEx Housing Affordability

This is not a full Django project, just an app to be included in an existing project.

## Setup and Installation 

1) Download (probably within a virtual environment used for an existing project): 
```
pip install git+https://github.com/govex/housing_affordability.git
```

2) Add to INSTALLED_APP of the Django Project settings module:
```python
# djangoproj/settings.py

INSTALLED_APPS = [
...
'housing_affordability',
...
]
```

3) Add to Django Project urls module:
```python
# djangoproj/urls.py

urlpatterns = [
...
path('analysis/housing/', include('housing_affordability.urls')),
...
]
```

4) Add a link to your template where ever appropriate (possibly a nav bar) that links to `/analysis/housing/`.

## TODO:

1) Continue to add, improve, and explain visualizations and UI/UX.
2) Clean up css which has a lot of unnecessary stuff because it was mostly grabbed from a different project.
3) If possible, set up URLs in templates to be robust to prefix from Project URLs (eg `/analysis/housing` in setup step 3)
4) Expand TODO
