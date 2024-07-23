import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Data

async def fetch_data(db: AsyncSession):
    query = select(Data)
    result = await db.execute(query)
    data = result.fetchall()

    data_frame = pd.DataFrame([{
        'id': row[0].id,
        'label': row[0].label,
        'value': row[0].value,
        'measured_at': row[0].measured_at
    } for row in data])
    return data_frame

def plot_time_series(data):
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='measured_at', y='value', data=data)
    plt.title('Time Series Data')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True)
    plt.savefig('output/time_series_plot.png')
    plt.close()

def plot_histogram(data):
    plt.figure(figsize=(10, 6))
    sns.histplot(data['value'], kde=True)
    plt.title('Histogram of Values')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig('output/histogram_plot.png')
    plt.close()

def plot_boxplot(data):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='measured_at', y='value', data=data)
    plt.title('Boxplot of Values Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True)
    plt.savefig('output/boxplot.png')
    plt.close()

async def generate_visualizations(db: AsyncSession):
    data = await fetch_data(db)
    plot_time_series(data)
    plot_histogram(data)
    plot_boxplot(data)


if __name__ == "__main__":
    db = next(get_db())
    generate_visualizations(db)