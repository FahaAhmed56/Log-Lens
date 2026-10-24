"""CLI: python -m loglens.cli --input data/sample_logs.csv --output results.csv"""
import argparse
from pathlib import Path
import pandas as pd
from .engine import analyze_logs, load_model

def main():
    p=argparse.ArgumentParser(description="LogLens offline anomaly scanner")
    p.add_argument("--input", required=True)
    p.add_argument("--output",default="results.csv")
    p.add_argument("--model",default="models/isolation_forest.joblib")
    args=p.parse_args()
    df=pd.read_csv(args.input)
    result=analyze_logs(df,load_model(args.model))
    result.to_csv(args.output,index=False)
    print(f"Processed {len(result)} logs; flagged {int(result['is_anomaly'].sum())} anomalies; saved {args.output}")
if __name__=="__main__":main()
