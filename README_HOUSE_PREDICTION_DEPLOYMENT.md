# House Prediction Deployment

This folder contains a dependency-free web deployment for the house price prediction section of `Oseagwina_COSC22404_Ass1.ipynb`.

## Run locally

```powershell
python house_prediction_app.py
```

Open:

```text
http://127.0.0.1:8000
```

If port `8000` is busy, choose another port:

```powershell
$env:PORT=8080
python house_prediction_app.py
```

## Web usage

Fill in the eight housing inputs:

- `MedInc`
- `HouseAge`
- `AveRooms`
- `AveBedrms`
- `Population`
- `AveOccup`
- `Latitude`
- `Longitude`

Then click **Predict price**.

## API usage

Endpoint:

```text
POST /api/predict
```

Example:

```powershell
$body = @{
  MedInc = 4.5
  HouseAge = 20
  AveRooms = 5.5
  AveBedrms = 1.0
  Population = 900
  AveOccup = 3.0
  Latitude = 34.05
  Longitude = -118.25
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/predict -Method Post -ContentType "application/json" -Body $body
```

## Notes

The app uses the same feature names, target conversion, and linear regression approach from the notebook. It embeds the fitted model coefficients so the deployment works without installing `pandas`, `scikit-learn`, Flask, or Streamlit.
