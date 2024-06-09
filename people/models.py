from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=7, unique=True)

    def __str__(self):
        return self.abbrev

class TrainingProgramme(models.Model):
    name = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=5)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.abbrev



class Tutor(AbstractUser):
    is_admin = models.BooleanField(default=False)
    department = models.CharField(max_length=7, choices=[
        ('gl', 'Génie Logiciel'),
        ('wme', 'Web and Mobile Engineering'),
        ('iad', 'Informatique et Aide à la Décision'),
        ('rc', 'Réseaux de communications'),
        ('ise', 'Ingénierie des Systèmes Embarqués'),
        ('lc', 'Langues et Communication')
    ], default='gl')
    semaine_type = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(53)], null=True, blank=True)






