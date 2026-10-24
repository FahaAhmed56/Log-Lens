import io
from pathlib import Path
import pandas as pd
import streamlit as st
from loglens.engine import analyze_logs, load_model

st.set_page_config(page_title="LogLens AI",page_icon="🔎",layout="wide")
st.title("🔎 LogLens AI — Log Anomaly Detection")
st.caption("Offline AI prototype. Anomalies are leads for investigation, not proof of incidents.")
file=st.file_uploader("Upload structured logs (CSV)",type=["csv"])
try:
    df=pd.read_csv(file if file else 'data/sample_logs.csv')
    @st.cache_resource
    def model():
        return load_model('models/isolation_forest.joblib')
    result=analyze_logs(df,model())
    a,b,c=st.columns(3)
    a.metric('Total events',len(result))
    b.metric('Flagged anomalies',int(result.is_anomaly.sum()))
    c.metric('Anomaly rate',f"{100*result.is_anomaly.mean():.1f}%")
    st.subheader('Anomaly score by event')
    chart=result[['timestamp','anomaly_score']].copy()
    chart.index=pd.to_datetime(chart.pop('timestamp'),utc=True)
    st.line_chart(chart)
    st.subheader('Events')
    only=st.checkbox('Show only anomalies',value=True)
    filtered=result[result.is_anomaly] if only else result
    st.dataframe(filtered.sort_values('anomaly_score',ascending=False),use_container_width=True)
    st.download_button('Download analyzed CSV',result.to_csv(index=False).encode(),file_name='analyzed_logs.csv',mime='text/csv')
    st.info('Supports the included sample format: timestamp, level, service, status, duration_ms, bytes_sent, message.')
except (ValueError, FileNotFoundError) as ex:
    st.error(str(ex))
