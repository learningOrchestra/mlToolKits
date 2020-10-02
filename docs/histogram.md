# Histogram microservice
Microservice used to make the histogram from a stored file, storing the resulting histogram in a new file in MongoDB.

## Create a Histogram from posted file
`POST CLUSTER_IP:5004/histograms/<filename>`

The request is sent in the body, `histogram_filename` is the name of the file in which the histogram result is saved to and `fields` is an array with all the fields necessary to make the histogram.

```json
{
    "histogram_filename": "filename_to_save_the_histogram",
    "fields": ["fields", "from", "filename"]
}
```
