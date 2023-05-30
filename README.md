# Flora-visualization

Application for visualizing the Floras inventory data on a map.

## Deployment

To run the app:

### Install dependences

python3 -m pip install -r requirements.txt

### Run dev
--server.baseUrlPath: Initial application path
--server.port: Port on which the app will be launched

```
streamlit run main.py --server.baseUrlPath=/services/flora/visualization --server.port=5025
```

### Docker

docker build -t app_flora_visualization:1.0.0 .
docker run --env-file ../.env -p 5015:8501 -d app_flora_visualization:1.0.0
