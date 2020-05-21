from data_loader import load_challenger_entries, load_challenger_summoners
import os

os.system('export GOOGLE_APPLICATION_CREDENTIALS="/home/sudarshan/projects/league-match-prediction/resources/league-predict-2c03cc0bac96.json"')
load_challenger_entries()
load_challenger_summoners()