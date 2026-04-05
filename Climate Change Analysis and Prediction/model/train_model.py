
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

data = pd.read_csv("data/climate_data.csv")

X = data[["Year","CO2","Sea_Level"]]
y = data["Temperature"]

model = RandomForestRegressor()
model.fit(X,y)

joblib.dump(model,"model/model.pkl")
print("Model trained!")
