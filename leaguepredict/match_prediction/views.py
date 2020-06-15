from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .util import get_participants, get_summoner_id


from .forms import SummonerNameForm


# Create your views here.
def index(request):
    submitted = False
    if request.method == 'POST':
        form = SummonerNameForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            sname = cd['summoner_name']
            return display(request, sname)
    else:
        form = SummonerNameForm()
        if 'submitted' in request.GET:
            submitted = True
        return render(request, "match_prediction/index.html", {'form': form, 'submitted': submitted})


def display(request, sname):
    participants = get_participants(sname)
    return render(request, "match_prediction/display.html", {'participants': participants})
