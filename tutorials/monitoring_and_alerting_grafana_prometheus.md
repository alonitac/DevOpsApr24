# Grafana and Prometheus

## Prometheus 

The Prometheus server is configured via command-line flags or a [configuration file](https://prometheus.io/docs/prometheus/latest/configuration/configuration/) (a.k.a. `prometheus.yml`). 

Let's start a Prometheus server as a Docker container with a simple configurations file:

```yaml
# grafana_prometheus/prometheus.yml

global:
  scrape_interval:     15s     # How often Prometheus will scrape targets

scrape_configs:
    
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']

  - job_name: node
    static_configs:
      - targets: ['localhost:9100']
```

The above configuration file can be found under `grafana_prometheus/prometheus.yml`.
The Prometheus was configured to monitor 2 resources:
 - The `prometheus` job with the HTTP target `localhost:9090`. This is a metrics exposed by the Prometheus server itself (yes it monitors its own health).
 - The `node` job with the HTTP target `localhost:9100`. This is a simple piece of software (called [Node Exporter](https://github.com/prometheus/node_exporter)) running on a Linux node and exposes a wide variety of hardware- and kernel-related metrics. 

What Prometheus essentially does is accessing `localhost:9090/metrics` and `localhost:9100/metrics` every 15 seconds, and collects the metrics values. 

> #### 🧐 Try it yourself 
> 
> Open up your web browser and visit `localhost:9090/metrics`. Take a look on the [metric data model format](https://prometheus.io/docs/concepts/data_model/) and the exposed metrics. 

```bash
cd grafana_prometheus
docker run -d --network host -p 9090:9090 --name prometheus -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml -v prometheus-data:/prometheus prom/prometheus
```

Now [follow the instructions here](https://prometheus.io/docs/guides/node-exporter/) to run the Node Exporter, so Prometheus can collect metrics on your local Linux node.

Finally, let's deploy a Grafana server: 

```bash 
docker run -d --net host -p 3000:3000 --name grafana -v grafana-data:/var/lib/grafana grafana/grafana
```

Let's visit the server in http://localhost:3000 (username and password are `admin`) and explore the metrics scraped by Prometheus. 

1. Configure Prometheus as a data source.
1. Click the menu icon and, in the sidebar, click **Explore**. The Prometheus data source will already be selected.
1. Confirm that you’re in code mode by checking the **Builder/Cod**e toggle at the top right corner of the query panel.
1. In the query editor, where it says _Enter a PromQL query..._, enter `node_cpu_seconds_total` and then press Shift + Enter. A graph appears.
1. Add the rate function to your query to visualize the rate of requests per second:

```text
rate(node_cpu_seconds_total[5m])
```

1. Add the sum aggregation operator to your query to group time series by `cpu`:

```text
sum(rate(node_cpu_seconds_total[5m])) by(cpu)
```

### Instrumenting a Flask webserver

Instrumentation is the process of adding custom code to track specific metrics within the application's code and exposing those metrics via an HTTP endpoint for Prometheus to scrape.

Prometheus is shipped official and unofficial [client libraries](https://prometheus.io/docs/instrumenting/clientlibs/) for most of common programing language. 

Let's follow the below instructions to instrument a simple Flask webserver. 

1. Take a look on the base code under `simple_flask_prometheus/`:
   - The code uses the official [Python client for Prometheus](https://prometheus.github.io/client_python/) library. 
   - You'll notice the below code snippet which exposes the `/metrics` endpoint to be scraped by Prometheus. 
       ```python
       app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
           '/metrics': make_wsgi_app()
       })
       ``` 
   - In the code there is a single metrics of type `Counter` which tracks the number of requests to the home (`/`) endpoint of the server.

2. Take a look at the example in https://prometheus.github.io/client_python/, and expose the following information to Prometheus:
   - Use the defined `requests_metric` metric to monitor all server endpoints, use [Labels](https://prometheus.github.io/client_python/instrumenting/labels/) to group different endpoints under the same metric name.
   - Use the [Summary metric](https://prometheus.github.io/client_python/instrumenting/summary/) to monitor the `predict()` function called in the `/upload` and `/api/upload` endpoints.
   - Use [Histogram](https://prometheus.github.io/client_python/instrumenting/histogram/) to monitor the time it takes to serve the `/` endpoint. 
   - Use [Gauge](https://prometheus.github.io/client_python/instrumenting/gauge/) to monitor the number of outstanding requests to the `/upload` endpoint ( the count of requests that have been received but have not yet been completed or responded to).
3. Edit `prometheus.yaml` configurations file to scrape your Flask server. 
4. Visualize in Grafana.

### Grafana alerting

Alerts let you know when something important happens in your system.
They help you find out about issues right away, so you can fix them before they become big problems.

Grafana allows you to configure alert rules based on your logs and metrics data.

Here are few examples for common alert rules: 

- **High CPU usage:** CPU of one of the machines in the system is high.
- **Too many requests:** One of the microservices is receiving too many requests.
- **Microservice Unavailability:** One of the microservices is down. 

#### Strawberry fields forever

Imagine you're part of an agri-tech company offering cloud-based services for monitoring vital metrics in strawberry fields.
Your platform collects real-time data on temperature and humidity, crucial factors for optimizing crop yield and health.

In this tutorial, we'll focus on configuring an alert rule for high temperatures, a common concern for strawberry farmers during hot weather.

1. Execute the Flask server under `weather_sensor_webserver/`. This server simulates a sensor gathering real-time weather data, including temperature and humidity readings from strawberry fields.

Your Prometheus server is now collecting the `current_temperature` and `current_humidity` metrics per field.

2. Follow [the official Grafana docs on how to configure alerts](https://grafana.com/docs/grafana/latest/alerting/set-up/) and create an alert that triggered upon high temperature value (E.g. `34`) for a certain period of time (E.g. during the last 5 minutes).
3. Test your alert by artificially send high values of temperature (change the code of `weather_sensor_webserver` accordingly) and expect an alert notification.



