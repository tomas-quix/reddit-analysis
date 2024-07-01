# Reddit Analysis

![Stars](https://img.shields.io/github/stars/tomas-quix/reddit-analysis)
![Forks](https://img.shields.io/github/forks/tomas-quix/reddit-analysis)

## Overview

As there are many elections around the world right now, I have put together this little stream processing pipeline to analyse Reddit data in real-time to measure how people react to unfolding situations during debates, election nights, etc. Feel free to fork it and change the analysis, right now it is a blend of ChatGPT and transformers. 

## Services

- **Reddit Data Collection**: Collect data from Reddit using the Reddit API.
- **Sentiment Analysis**: Analyze the sentiment of Reddit posts and comments.
- **Word Ranking**: Rank words based on their frequency and significance.
- **Dashboard**: Streamlit dashboard to visualise results

## Installation

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)

### Installation Steps
1. Clone this repository.
2. Ensure you have Python 3.8+ installed.

## Usage

### How to Run the Pipeline
To run the pipeline, you need to deploy the services defined in the `quix.yaml` file. 

To run pipeline using docker compose run QuixCLI command:
```
quix pipeline up
```
or directly docker compose file:
```
docker-compose build
docker-compose up
```
