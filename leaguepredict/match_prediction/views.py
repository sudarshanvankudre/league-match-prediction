from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import SummonerNameForm


# Create your views here.
def index(request):
    return render(request, "match_prediction/index.html")


def display_sname(request, sname):
    return HttpResponse("Hello {}!".format(sname))
