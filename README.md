# greensenti-visualization
To run the app just run:

```
streamlit run main.py

```

## DOCKER

### Build

To build the image you will need to add a folder called `data` with the following files:
 * results.csv 
 * vegetationindex.csv

```
docker build -t app_greensenti_visualize:1.0.1 -f GREENSENTI-VISUALIZE.dockerfile .
```

### Run


After that, create a `.env` file and fill the environment variables from the provided template.

Then, run the docker container as follows

```
docker run -p 8501:8501 --env-file .env -d app_greensenti_visualize:1.0.1

```
