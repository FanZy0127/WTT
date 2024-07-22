import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Data

def fetch_data(db: Session):
    return pd.read_sql(db.query(Data).statement, db.bind)

def plot_time_series(data):
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='measured_at', y='value', data=data)
    plt.title('Time Series Data')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True)
    plt.savefig('/tmp/time_series_plot.png')
    plt.close()

def plot_histogram(data):
    plt.figure(figsize=(10, 6))
    sns.histplot(data['value'], kde=True)
    plt.title('Histogram of Values')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig('/tmp/histogram_plot.png')
    plt.close()

def plot_boxplot(data):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='measured_at', y='value', data=data)
    plt.title('Boxplot of Values Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True)
    plt.savefig('/tmp/boxplot.png')
    plt.close()

async def generate_visualizations(db: Session):
    data = fetch_data(db)
    plot_time_series(data)
    plot_histogram(data)
    plot_boxplot(data)

if __name__ == "__main__":
    db = next(get_db())
    generate_visualizations(db)
