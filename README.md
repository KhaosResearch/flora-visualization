# Flora-visualization

Application for visualizing the Floras inventory data on a map.

## Deployment

To run the app:

### Install dependences

```bash
python3 -m pip install -r requirements.txt
```

### Run dev

Create a `.env` file similar to `.env.template` and fill in the values.

`--server.baseUrlPath`: Initial application path
`--server.port`: Port on which the app will be launched

```bash
streamlit run main.py --server.baseUrlPath=/services/flora/visualization --server.port=5025
```

### Docker

```bash
docker build -t app_flora_visualization:1.0.0 .
docker run --env-file ../.env -p 5025:8501 -d app_flora_visualization:1.0.0

