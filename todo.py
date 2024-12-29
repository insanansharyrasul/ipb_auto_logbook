# Add this code block if time input is behaving unexpectedly
import pandas as pd
from datetime import datetime, time
df = pd.read_csv('a.csv')

for i in range(df.shape[0]):
    mulai = df['mulai'][i].split(':')
    selesai = df['selesai'][i].split(':')
    now = datetime.now().strftime("%H:M").split(':')
    if (time(int(now[0], int(now[1]))) > time(int(selesai[0]), int(selesai[1]))):
        pass
