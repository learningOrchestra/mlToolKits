# Histogram microservice
Microservice used to make the histogram from stored file, storing the result in a new file in MongoDB.

## Create an Histogram from inserted file
`POST CLUSTER_IP:5004/histograms`

The request is sent in body, the filename is the file to be maked the histogram, histrogram_filename is the filename to save the histogram result and fields are an array whith all fields to be maked the histogram.

```json
{
    "filename": "filename_to_make_histogram",
    "histogram_filename": "filename_to_save_the_histogram",
    "fields": ["fields", "from", "filename"]
}
```
