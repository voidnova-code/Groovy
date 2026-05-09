from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv

from game.models import GameRoom, GameMove


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Custom admin dashboard with stats and analytics"""
    # Basic stats
    total_users = User.objects.count()
    total_games = GameRoom.objects.count()
    active_games = GameRoom.objects.filter(status='playing').count()
    finished_games = GameRoom.objects.filter(status='finished').count()
    draws = GameRoom.objects.filter(is_draw=True).count()

    # Weekly stats (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    weekly_users = User.objects.filter(date_joined__gte=week_ago).count()
    weekly_games = GameRoom.objects.filter(created_at__gte=week_ago).count()

    # Daily game stats for chart (last 7 days)
    daily_stats = []
    for i in range(6, -1, -1):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        games_count = GameRoom.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count()
        daily_stats.append({
            'date': day.strftime('%a'),
            'games': games_count
        })

    # Recent games
    recent_games = GameRoom.objects.order_by('-created_at')[:10]

    # Top winners
    top_winners = User.objects.annotate(
        win_count=Count('wins')
    ).filter(win_count__gt=0).order_by('-win_count')[:5]

    # Most active players
    most_active = User.objects.annotate(
        games_played=Count('games_as_x') + Count('games_as_o')
    ).filter(games_played__gt=0).order_by('-games_played')[:5]

    context = {
        'total_users': total_users,
        'total_games': total_games,
        'active_games': active_games,
        'finished_games': finished_games,
        'draws': draws,
        'weekly_users': weekly_users,
        'weekly_games': weekly_games,
        'daily_stats': daily_stats,
        'recent_games': recent_games,
        'top_winners': top_winners,
        'most_active': most_active,
    }
    return render(request, 'admin/dashboard.html', context)


@user_passes_test(is_admin)
def admin_users(request):
    """Manage all users"""
    search = request.GET.get('search', '')
    if search:
        users = User.objects.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        ).order_by('-date_joined')
    else:
        users = User.objects.order_by('-date_joined')
    return render(request, 'admin/users.html', {'users': users, 'search': search})


@user_passes_test(is_admin)
def admin_games(request):
    """Manage all games"""
    status_filter = request.GET.get('status')
    search = request.GET.get('search', '')
    games = GameRoom.objects.all()

    if status_filter:
        games = games.filter(status=status_filter)
    if search:
        games = games.filter(
            Q(code__icontains=search) |
            Q(player_x__username__icontains=search) |
            Q(player_o__username__icontains=search)
        )

    return render(request, 'admin/games.html', {
        'games': games,
        'status_filter': status_filter,
        'search': search
    })


@user_passes_test(is_admin)
def admin_game_detail(request, game_id):
    """View game details and moves"""
    try:
        game = GameRoom.objects.get(id=game_id)
        moves = GameMove.objects.filter(room=game).order_by('move_number')
        return render(request, 'admin/game_detail.html', {'game': game, 'moves': moves})
    except GameRoom.DoesNotExist:
        return redirect('admin_games')


@user_passes_test(is_admin)
def admin_feedbacks(request):
    """View all feedbacks"""
    # Create a Feedback model in production
    feedbacks = []
    return render(request, 'admin/feedbacks.html', {'feedbacks': feedbacks})


@user_passes_test(is_admin)
def admin_create_user(request):
    """Create a new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if username and password:
            if User.objects.filter(username=username).exists():
                return render(request, 'admin/user_form.html', {'error': 'Username already exists!'})
            user = User.objects.create_user(username=username, email=email, password=password)
            return redirect('admin_users')
        return render(request, 'admin/user_form.html', {'error': 'Please fill all required fields!'})

    return render(request, 'admin/user_form.html')


@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    """Edit a user"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('admin_users')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        is_superuser = request.POST.get('is_superuser') == 'on'

        user.username = username
        user.email = email
        user.is_superuser = is_superuser
        user.save()

        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
            user.save()

        return redirect('admin_users')

    return render(request, 'admin/user_form.html', {'edit_user': user})


@user_passes_test(is_admin)
def delete_user(request, user_id):
    """Delete a user"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user.id == request.user.id:
                auth_logout(request)
            # Delete related games
            GameRoom.objects.filter(player_x=user).delete()
            GameRoom.objects.filter(player_o=user).delete()
            user.delete()
        except User.DoesNotExist:
            pass
    return redirect('admin_users')


@user_passes_test(is_admin)
def delete_game(request, game_id):
    """Delete a game"""
    if request.method == 'POST':
        try:
            game = GameRoom.objects.get(id=game_id)
            game.delete()
        except GameRoom.DoesNotExist:
            pass
    return redirect('admin_games')


@user_passes_test(is_admin)
def export_users(request):
    """Export users as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Date Joined', 'Last Login', 'Is Staff', 'Is Superuser'])

    for user in User.objects.all():
        writer.writerow([
            user.id,
            user.username,
            user.email or '',
            user.date_joined.strftime('%Y-%m-%d %H:%M'),
            user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
            user.is_staff,
            user.is_superuser
        ])

    return response


@user_passes_test(is_admin)
def export_games(request):
    """Export games as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="games.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Code', 'Player X', 'Player O', 'Status', 'Winner', 'Is Draw', 'Created'])

    for game in GameRoom.objects.all():
        writer.writerow([
            game.id,
            game.code,
            game.player_x.username,
            game.player_o.username if game.player_o else '',
            game.status,
            game.winner.username if game.winner else '',
            game.is_draw,
            game.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response


@user_passes_test(is_admin)
def admin_settings(request):
    """View and edit system settings"""
    # In a real app, you'd use django-settings or database for this
    settings_data = {
        'allow_registration': True,
        'max_room_idle_hours': 24,
        'auto_delete_finished': True,
    }
    return render(request, 'admin/settings.html', {'settings': settings_data})


@user_passes_test(is_admin)
def admin_clear_data(request):
    """Delete all non-admin data from the database. Only accessible by superusers via POST."""
    if request.method == 'POST':
        # Keep all superuser accounts; delete other users and app data
        try:
            # Delete game moves and rooms
            GameMove.objects.all().delete()
            GameRoom.objects.all().delete()

            # Delete non-superuser users
            User.objects.filter(is_superuser=False).delete()

            # Optionally: if there are other app models, delete them here
        except Exception:
            # If any error, continue but log or ignore silently for now
            pass

        # Redirect back to settings
        return redirect('admin_settings')

    # Non-POST -> redirect
    return redirect('admin_settings')


@user_passes_test(is_admin)
def admin_logs(request):
    """View activity logs"""
    # Mock logs - in production, create a Log model
    logs = []
    return render(request, 'admin/logs.html', {'logs': logs})


def admin_google_auth(request):
    """Handle Google OAuth for admin login"""
    from django.http import JsonResponse
    from django.contrib.auth import login
    from game.auth_google import GoogleAuthHandler
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            auth_code = data.get('auth_code')
            redirect_uri = data.get('redirect_uri')

            if not auth_code or not redirect_uri:
                return JsonResponse(
                    {'error': 'Missing auth_code or redirect_uri'},
                    status=400
                )

            handler = GoogleAuthHandler()
            user_data, tokens, error = handler.authenticate_with_google(
                auth_code,
                redirect_uri,
                email_to_link=None
            )

            if error:
                return JsonResponse({'error': error}, status=400)

            # Get the user object
            try:
                user = User.objects.get(id=user_data['id'])
                
                # Check if superuser
                if not user.is_superuser:
                    return JsonResponse(
                        {'error': 'Only admin users can access this panel'},
                        status=403
                    )
                
                # Create Django session (not JWT for admin)
                login(request, user)
                
                return JsonResponse({
                    'success': True,
                    'user': user_data,
                    'redirect': '/admin/dashboard/'
                })
            except User.DoesNotExist:
                return JsonResponse(
                    {'error': 'User account not found'},
                    status=404
                )

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)