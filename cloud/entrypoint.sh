#!/bin/bash --login
conda activate neon
bokeh serve --port $PORT demo --allow-websocket-origin $HOST
