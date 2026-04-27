from django.db import models

# Create your models here.

class DomainWeight(models.Model):
    building_type = models.TextField()
    zone = models.TextField()
    domain = models.TextField()
    dw_cr1 = models.FloatField() 
    dw_cr2 = models.FloatField() 
    dw_cr3 = models.FloatField() 
    dw_cr4 = models.FloatField() 
    dw_cr5 = models.FloatField() 
    dw_cr6 = models.FloatField() 
    dw_cr7 = models.FloatField() 


class ImpactWeight(models.Model):
    building_type = models.TextField()
    zone = models.TextField()
    imp_cr1 = models.FloatField()
    imp_cr2 = models.FloatField()  
    imp_cr3 = models.FloatField() 
    imp_cr4 = models.FloatField()
    imp_cr5 = models.FloatField()
    imp_cr6 = models.FloatField()
    imp_cr7 = models.FloatField()


class Levels(models.Model):
    code = models.TextField()
    level_desc = models.TextField()
    desc = models.TextField()
    score_cr1  = models.IntegerField()
    score_cr2 = models.IntegerField()
    score_cr3 =models.IntegerField()
    score_cr4 =models.IntegerField()
    score_cr5 =models.IntegerField()
    score_cr6 =models.IntegerField()
    score_cr7 =models.IntegerField()
    level = models.IntegerField()
    mandatory = models.IntegerField()
    domain = models.TextField()



class Services(models.Model):
    domain = models.TextField()
    code = models.TextField()
    service_group = models.TextField()
    service_desc = models.TextField()

class Costs(models.Model):
    name = models.TextField()
    services = models.TextField()
    cost = models.TextField()
    desc = models.TextField()
    img = models.TextField()
    con = models.TextField()