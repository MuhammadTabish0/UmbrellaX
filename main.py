import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
a = pd.read_csv('synthetic_covid19_data.csv')
plt.plot(a['location'], a['new_cases'], label='Cases')
plt.show()