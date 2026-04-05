from sklearn.ensemble import RandomForestRegressor
import joblib

def train_model(df):
    X = df[["Year","CO2","Sea"]]
    y = df["Temperature"]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )

    model.fit(X,y)
    joblib.dump(model,"model/model.pkl")