"""
App Models
Create your models in here
"""

# Django
from itertools import count
from django.db import models

class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (
            ("manage_afctrack", "Can manage the afctrack APP"),
            ("jfc_access", "Can see his own Information"),
            ("fc_access", "Can see the Activity of every FC and JFC"),
        )
        verbose_name = "afctrack"
    
class MonthlyFCPayment(models.Model):
    character_id = models.IntegerField(verbose_name="Character ID", black=False)
    month = models.IntegerField(verbose_name="Taxed month", blank=False, default=0)
    year = models.IntegerField(verbose_name="Taxed year", blank=False, default=0)
    player_name = models.IntegerField(verbose_name="Player Name", blank=False)
    payment_value = models.IntegerField(verbose_name="Payment Ammount", blank=False, default=0)
    fleet_ammount = models.IntegerField(verbose_name="Fleet Ammount", blank=False, default=0)

class AtatFatlink(models.Model):
    creator_id = models.IntegerField(verbose_name="Creator ID")  # Player ID
    fleet_id = models.IntegerField(verbose_name="Fleet ID")

    class Meta:
        db_table = 'atat_fatlink'  # Ensure this matches the actual table name in the database

# Get all the players (creator_id) and count the number of fleets they have created
fleet_counts = AtatFatlink.objects.values('creator_id')\
                                   .annotate(fleet_count=count('fleet_id'))\
                                   .order_by('-fleet_count')

# Print the results
for player in fleet_counts:
    print(f"Creator ID: {player['creator_id']}, Fleets Created: {player['fleet_count']}")