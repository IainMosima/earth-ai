# Earth-AI API Endpoints Documentation

This document lists all available endpoints in the Earth-AI project and provides examples of how to use them with synthetic data.

## Data Ingestion Endpoints

### 1. `/api/v1/data/upload`
- **Method**: POST
- **Description**: Upload satellite imagery or environmental data
- **Parameters**:
  - `data_type`: Type of data (satellite, sensor, weather)
  - `timestamp`: Data collection timestamp
  - `location`: Coordinates or region name
- **Example with synthetic data**:
```python
import requests
import json
from synthetic_data_generator import generate_satellite_imagery

# Generate synthetic satellite data
synthetic_data = generate_satellite_imagery(
    resolution="medium", 
    cloud_coverage=0.3
)

# Upload the synthetic data
response = requests.post(
    "http://localhost:8000/api/v1/data/upload",
    json={
        "data_type": "satellite",
        "timestamp": "2023-10-15T14:30:00Z",
        "location": "34.0522,-118.2437",
        "data": synthetic_data
    }
)
print(response.json())
```

### 2. `/api/v1/data/batch-upload`
- **Method**: POST
- **Description**: Upload multiple datasets at once
- **Parameters**:
  - `datasets`: Array of data objects with types and metadata
- **Example with synthetic data**:
```python
from synthetic_data_generator import generate_batch_data

# Generate synthetic batch data
batch_data = generate_batch_data(
    num_samples=5,
    data_types=["satellite", "weather", "sensor"]
)

# Upload batch data
response = requests.post(
    "http://localhost:8000/api/v1/data/batch-upload",
    json={"datasets": batch_data}
)
print(response.json())
```

## Analysis Endpoints

### 3. `/api/v1/analysis/land-cover`
- **Method**: POST
- **Description**: Analyze land cover classification from imagery
- **Parameters**:
  - `image_data`: Image data or reference ID
  - `algorithm`: Classification algorithm to use
- **Example with synthetic data**:
```python
from synthetic_data_generator import generate_satellite_imagery

synthetic_image = generate_satellite_imagery(
    resolution="high", 
    bands=["visible", "infrared"]
)

response = requests.post(
    "http://localhost:8000/api/v1/analysis/land-cover",
    json={
        "image_data": synthetic_image,
        "algorithm": "random_forest"
    }
)
print(response.json())
```

### 4. `/api/v1/analysis/change-detection`
- **Method**: POST
- **Description**: Detect changes between two time periods
- **Parameters**:
  - `baseline_data`: Image data from first time period
  - `comparison_data`: Image data from second time period
  - `sensitivity`: Detection sensitivity (0.0-1.0)
- **Example with synthetic data**:
```python
from synthetic_data_generator import generate_temporal_data_pair

# Generate synthetic temporal data pair
baseline, comparison = generate_temporal_data_pair(
    region_type="forest",
    change_magnitude=0.4
)

response = requests.post(
    "http://localhost:8000/api/v1/analysis/change-detection",
    json={
        "baseline_data": baseline,
        "comparison_data": comparison,
        "sensitivity": 0.7
    }
)
print(response.json())
```

## Prediction Endpoints

### 5. `/api/v1/predict/deforestation`
- **Method**: POST
- **Description**: Predict future deforestation risk
- **Parameters**:
  - `region`: Geographic region for prediction
  - `historical_data`: Time series data or reference IDs
  - `timeframe`: Future prediction timeframe in months
- **Example with synthetic data**:
```python
from synthetic_data_generator import generate_historical_forest_data

historical_data = generate_historical_forest_data(
    num_timepoints=12,
    deforestation_trend="accelerating"
)

response = requests.post(
    "http://localhost:8000/api/v1/predict/deforestation",
    json={
        "region": "amazon_basin_subset",
        "historical_data": historical_data,
        "timeframe": 6
    }
)
print(response.json())
```

### 6. `/api/v1/predict/crop-yield`
- **Method**: POST
- **Description**: Predict agricultural crop yield
- **Parameters**:
  - `crop_type`: Type of crop
  - `region`: Geographic region for prediction
  - `climate_data`: Weather/climate data
  - `soil_data`: Soil quality indicators
- **Example with synthetic data**:
```python
from synthetic_data_generator import generate_agricultural_data

climate_data, soil_data = generate_agricultural_data(
    crop_type="wheat",
    climate_condition="drought"
)

response = requests.post(
    "http://localhost:8000/api/v1/predict/crop-yield",
    json={
        "crop_type": "wheat",
        "region": "midwest_us",
        "climate_data": climate_data,
        "soil_data": soil_data
    }
)
print(response.json())
```

## Data Retrieval Endpoints

### 7. `/api/v1/data/{data_id}`
- **Method**: GET
- **Description**: Retrieve specific data by ID
- **Parameters**:
  - `data_id`: Unique identifier for the data
- **Example**:
```python
response = requests.get(
    "http://localhost:8000/api/v1/data/12345"
)
print(response.json())
```

### 8. `/api/v1/data/query`
- **Method**: GET
- **Description**: Query data based on parameters
- **Parameters**:
  - `data_type`: Type of data to retrieve
  - `start_date`: Beginning of time range
  - `end_date`: End of time range
  - `region`: Geographic area
- **Example**:
```python
response = requests.get(
    "http://localhost:8000/api/v1/data/query",
    params={
        "data_type": "satellite",
        "start_date": "2023-01-01",
        "end_date": "2023-06-30",
        "region": "california"
    }
)
print(response.json())
```

## Model Management Endpoints

### 9. `/api/v1/models/train`
- **Method**: POST
- **Description**: Train a new model on provided data
- **Parameters**:
  - `model_type`: Type of model to train
  - `training_data`: Data for training or reference IDs
  - `parameters`: Model hyperparameters
- **Example with synthetic data**:
```python
from synthetic_data_generator import generate_training_dataset

training_data = generate_training_dataset(
    dataset_size="medium",
    feature_noise=0.1,
    label_type="classification"
)

response = requests.post(
    "http://localhost:8000/api/v1/models/train",
    json={
        "model_type": "forest_cover_classifier",
        "training_data": training_data,
        "parameters": {
            "max_depth": 10,
            "n_estimators": 100
        }
    }
)
print(response.json())
```

### 10. `/api/v1/models/{model_id}/predict`
- **Method**: POST
- **Description**: Use a specific model to make predictions
- **Parameters**:
  - `model_id`: ID of the model to use
  - `input_data`: Data to make predictions on
- **Example with synthetic data**:
```python
from synthetic_data_generator import generate_prediction_features

input_features = generate_prediction_features(
    num_samples=5,
    feature_type="spectral_indices"
)

response = requests.post(
    "http://localhost:8000/api/v1/models/forest-model-v2/predict",
    json={
        "input_data": input_features
    }
)
print(response.json())
```

## Visualization Endpoints

### 11. `/api/v1/visualize/map`
- **Method**: GET
- **Description**: Generate map visualization of data
- **Parameters**:
  - `data_id`: ID of data to visualize
  - `visualization_type`: Type of visualization
  - `color_scheme`: Color scheme to use
- **Example**:
```python
response = requests.get(
    "http://localhost:8000/api/v1/visualize/map",
    params={
        "data_id": "analysis_result_12345",
        "visualization_type": "heatmap",
        "color_scheme": "viridis"
    }
)
# Response contains URL to rendered visualization
print(response.json())
```

### 12. `/api/v1/visualize/timeseries`
- **Method**: POST
- **Description**: Generate time series visualization
- **Parameters**:
  - `data`: Array of time series data points or reference IDs
  - `metrics`: Metrics to visualize
- **Example with synthetic data**:
```python
from synthetic_data_generator import generate_timeseries_data

timeseries_data = generate_timeseries_data(
    duration_months=24,
    metrics=["ndvi", "precipitation", "temperature"]
)

response = requests.post(
    "http://localhost:8000/api/v1/visualize/timeseries",
    json={
        "data": timeseries_data,
        "metrics": ["ndvi", "precipitation"]
    }
)
# Response contains URL to visualization or visualization data
print(response.json())
```
