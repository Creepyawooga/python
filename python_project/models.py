from django.db import models

class Vacancy(models.Model):
    name = models.TextField()
    key_skills = models.TextField()
    salary_from = models.FloatField()
    salary_to = models.FloatField()
    salary_currency = models.TextField()
    area_name = models.TextField()
    published_at = models.TextField()

    class Meta:
        db_table = 'vacancies'
