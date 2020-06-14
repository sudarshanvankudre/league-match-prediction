from django import forms


class SummonerNameForm(forms.Form):
    summoner_name = forms.CharField(label="Your Summoner Name", max_length=100)
