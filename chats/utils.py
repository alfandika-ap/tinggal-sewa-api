from django.contrib.auth.models import User
from django.db.models import Sum

from .models import ChatMessages


def dashboard_callback(request, context):
    """
    Dashboard callback function for the Unfold admin.
    Provides token usage stats for the admin dashboard.
    """
    # Get total token usage across all users
    total_token_usage = ChatMessages.objects.aggregate(total=Sum('token_usage'))['total'] or 0
    
    # Get token usage stats for individual users
    users_token_usage = ChatMessages.objects.values('user__username').annotate(
        total=Sum('token_usage')
    ).order_by('-total')

    # Filter by specific user if in the request
    filtered_user_id = request.GET.get('user__id__exact')
    filtered_user_token_usage = None
    filtered_user_name = None
    
    if filtered_user_id:
        try:
            # Get token usage for the filtered user
            filtered_user = User.objects.get(id=filtered_user_id)
            filtered_user_name = filtered_user.username
            filtered_user_token_usage = ChatMessages.objects.filter(
                user_id=filtered_user_id
            ).aggregate(total=Sum('token_usage'))['total'] or 0
        except User.DoesNotExist:
            pass

    context.update({
        'total_token_usage': total_token_usage,
        'users_token_usage': users_token_usage,
        'filtered_user_token_usage': filtered_user_token_usage,
        'filtered_user_name': filtered_user_name,
    })
    
    return context 