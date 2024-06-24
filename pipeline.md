```mermaid
%%{ init: { 'flowchart': { 'curve': 'monotoneX' } } }%%
graph LR;
reddit-source[reddit-source] -->|reddit-raw|sentiment-analysis[sentiment-analysis];
reddit-source[reddit-source] -->|reddit-raw|words-ranking[words-ranking];
words-ranking[words-ranking] -->|words-count|influxdb-3-destination[influxdb-3-destination];
sentiment-average[sentiment-average]

```