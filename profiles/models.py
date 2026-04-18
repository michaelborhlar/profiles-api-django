from django.db import models


class Profile(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    gender = models.CharField(max_length=50)
    gender_probability = models.FloatField()
    sample_size = models.IntegerField()
    age = models.IntegerField()
    age_group = models.CharField(max_length=20)
    country_id = models.CharField(max_length=10)
    country_probability = models.FloatField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return self.name
