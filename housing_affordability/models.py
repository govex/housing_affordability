from django.db import models
from django.core.exceptions import ValidationError
import datetime
import re


class Government(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200, null=True, blank=True)
    state_abbr = models.CharField(max_length=2, null=True, blank=True)
    country_abbr = models.CharField(max_length=3, default='USA')
    state_fip = models.CharField(max_length=2, null=True, blank=True)
    place_fip = models.CharField(max_length=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return(self.name)

    # want to confirm unique state_fip/place_fip pairs but all multiple null/null
    # of those for foreign or different level govs
    def validate_unique(self, exclude=None):
        if self.country_abbr == 'USA' and \
           Government.objects.exclude(id=self.id) \
                             .filter(state_fip=self.state_fip, place_fip=self.place_fip)\
                             .exists():
            raise ValidationError('Cannot have multiple Governments from USA with same state_fip/place_fip pair')
        super(Government, self).validate_unique(exclude=exclude)

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(Government, self).save(*args, **kwargs)

class Gov_Demographics_Source(models.Model):
    year = models.IntegerField()
    var_name = models.CharField(max_length=50)
    source = models.CharField(max_length=200)
    source_variable = models.CharField(max_length=200)
    description = models.TextField()
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('year', 'var_name'),)
        ordering = ['year', 'var_name']

    def __str__(self):
        return('{} -- {}'.format(self.year, self.var_name))
    

class Gov_Demographic(models.Model):
    gov = models.ForeignKey('Government',
                            on_delete=models.CASCADE)
    var = models.ForeignKey('Gov_Demographics_Source',
                               on_delete=models.CASCADE)
    value = models.FloatField(null=True, blank=True)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = (('gov', 'var'),)
        ordering = ['gov', 'var']
        
    def __str__(self):
        return('{} -- {} -- {}'.format(self.var.year, self.var.var_name, self.gov.name))

