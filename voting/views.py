from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import redirect, render

from .models import Candidate, Position, Vote


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    voted_ids = set(
        Vote.objects.filter(voter=request.user).values_list('position_id', flat=True)
    )
    positions = []
    for p in Position.objects.all():
        positions.append({
            'position': p,
            'voted': p.id in voted_ids,
        })
    return render(request, 'home.html', {'positions': positions})


@login_required
def ballot(request):
    voted_ids = Vote.objects.filter(voter=request.user).values_list(
        'position_id', flat=True
    )
    positions = list(
        Position.objects.filter(is_open=True)
        .exclude(id__in=voted_ids)
        .prefetch_related('candidates')
    )

    if request.method == 'POST':
        saved = 0
        for position in positions:
            candidate_id = request.POST.get(f'position_{position.id}')
            if not candidate_id:
                continue
            candidate = Candidate.objects.filter(
                id=candidate_id, position=position
            ).first()
            if candidate is None:
                continue
            try:
                with transaction.atomic():
                    Vote.objects.create(
                        voter=request.user, position=position, candidate=candidate
                    )
                saved += 1
            except IntegrityError:
                pass  # already voted for this position

        if saved:
            messages.success(request, f"Your vote was recorded for {saved} position(s).")
        else:
            messages.info(request, "No votes were submitted.")
        return redirect('home')

    return render(request, 'ballot.html', {'positions': positions})


@staff_member_required
def results(request):
    data = []
    for p in Position.objects.all():
        candidates = p.candidates.annotate(total=Count('vote')).order_by('-total')
        data.append({
            'position': p,
            'candidates': candidates,
            'total': sum(c.total for c in candidates),
        })
    return render(request, 'results.html', {'data': data})