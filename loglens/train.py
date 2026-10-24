from pathlib import Path
import joblib
import pandas as pd
from .engine import train_model

def main():
    model=train_model(pd.read_csv('data/sample_logs.csv'))
    Path('models').mkdir(exist_ok=True)
    joblib.dump(model,'models/isolation_forest.joblib')
    print('Saved models/isolation_forest.joblib')
if __name__=='__main__':main()
