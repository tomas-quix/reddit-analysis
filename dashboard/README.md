# Streamlit

[This code sample](https://github.com/quixio/quix-samples/tree/develop/python/destinations/streamlit) demonsrates how to run a Streamlit real-time dashboard that displays data from a Kafka topic.

You only need to edit the dashboard code if you want to update the layout, otherwise it works out of the box as a quick way to visualize your data.

Note that the code expects a timestamp in one of these columns: "timestamp", "Timestamp", "time", "ts"

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

This code sample uses the following environment variables:

- **input**: The topic to stream data from (`f1-data`)

## Requirements

Deploy the `Demo Data` source from the Quix Code Samples. This will stream Codemasters&reg; F1&reg; 2019 telemetry data into a topic called `f1-data`

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.