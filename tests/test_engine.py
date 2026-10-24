import pandas as pd
import pytest
from loglens.engine import prepare,train_model,analyze_logs
@pytest.fixture
def df():
    return pd.read_csv('data/sample_logs.csv')
def test_preparation(df):
    assert {'hour','is_error','is_slow','message_length'}.issubset(prepare(df).columns)
def test_model_prediction(df):
    out=analyze_logs(df,train_model(df))
    assert len(out)==len(df)
    assert out.is_anomaly.dtype==bool
    assert out['anomaly_score'].notna().all()
def test_missing_column(df):
    with pytest.raises(ValueError,match='Missing columns'): prepare(df.drop(columns=['status']))
def test_bad_timestamp(df):
    df.loc[0,'timestamp']='no-date'
    with pytest.raises(ValueError,match='timestamps'): prepare(df)
def test_negative_duration(df):
    df.loc[0,'duration_ms']=-3
    with pytest.raises(ValueError,match='non-negative'): prepare(df)
def test_small_training_set(df):
    with pytest.raises(ValueError,match='20'):train_model(df.head(5))
def test_anomaly_reason(df):
    df.loc[0,'status']=503
    result=analyze_logs(df,train_model(df))
    assert 'server error status' in result.loc[0,'reason']
