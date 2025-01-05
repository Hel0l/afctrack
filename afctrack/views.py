from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from afat.models import FatLink
from django.conf import settings
from datetime import datetime

# Doctrine points
POINTS = {
    'PCT/Roam': 0.5,
    'Strat OP': 1,
    'Hive': 1.5
}

@login_required
@permission_required("afctrack.fc_access", raise_exception=True)
def index(request):
    """
    Index view that displays fleet counts per player.
    """
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Get the primary keys of users in the "jfc" or "fc" groups
    fc_users_ids = User.objects.filter(groups__name__in=["jfc", "fc"]).values_list('id', flat=True)

    # Filter FatLink by those users and the current month/year
    fleet_counts = FatLink.objects.filter(
        creator_id__in=fc_users_ids,
        created__month=current_month,
        created__year=current_year
    ).values('creator_id__username', 'fleet_type')\
     .annotate(fleet_count=Count('id'))\
     .order_by('creator_id__username', 'fleet_type')  # Group by player and fleet type

    # Prepare the fleet data with aggregated information for each player
    player_data = {}

    for player in fleet_counts:
        player_name = player['creator_id__username']
        fleet_type = player['fleet_type']
        fleet_count = player['fleet_count']

        # Get points for the doctrine
        fleet_points = POINTS.get(fleet_type, 0)

        if player_name not in player_data:
            player_data[player_name] = {
                'total_fleet_count': 0,
                'total_fleet_points': 0,
                'fleet_count_by_type': {},  # Store fleet counts by type for display
            }

        # Accumulate fleet counts and points for the player
        player_data[player_name]['total_fleet_count'] += fleet_count
        player_data[player_name]['total_fleet_points'] += fleet_points * fleet_count

        # Accumulate fleet counts by type for displaying in the template
        if fleet_type not in player_data[player_name]['fleet_count_by_type']:
            player_data[player_name]['fleet_count_by_type'][fleet_type] = 0
        player_data[player_name]['fleet_count_by_type'][fleet_type] += fleet_count

    # Now that we have the total fleet counts and points for each player,
    # calculate payments for each player.
    total_score = sum(player['total_fleet_points'] for player in player_data.values())
    budget = float(request.GET.get('budget', 3000000000))

    # Calculate ISK per point if the total score is greater than 0
    if total_score > 0:
        isk_per_point = budget / total_score
    else:
        isk_per_point = 0

    # Calculate payment for each player
    for player_name, data in player_data.items():
        data['payment'] = data['total_fleet_points'] * isk_per_point

    # Get fleet count per doctrine and type for displaying in the template
    fleet_count_doctrine = FatLink.objects.filter(
        creator_id__in=fc_users_ids,
        created__month=current_month,
        created__year=current_year
    ).values('doctrine')\
     .annotate(doctrine_count=Count('id'))\
     .order_by('-doctrine_count')

    fleet_count_type = FatLink.objects.filter(
        creator_id__in=fc_users_ids,
        created__month=current_month,
        created__year=current_year
    ).values('fleet_type')\
     .annotate(type_count=Count('id'))\
     .order_by('-type_count')

    # Prepare the context for rendering the template
    context = {
        "player_data": player_data,  # Pass the aggregated player data to the template
        "fleet_count_doctrine": fleet_count_doctrine,  # Fleet count per doctrine
        "fleet_count_type": fleet_count_type  # Fleet count per type
    }

    # Render the template with the context
    return render(request, 'afctrack/index.html', context)
