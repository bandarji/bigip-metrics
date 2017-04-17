# F5 Networks BIG-IP Metrics Processing

## Purpose

Program collects metrics from BIG-IP targets. Right now, it only pulls
virtual services metrics, with WaveFront-formatted output (tcollector).

## Requirements

This uses my `auzaar` package. I do not have that package available via pip, yet.

## Execution

Program requires a single command line argument, the target cluster name,
matching an entry in `./bigip_metrics.yaml`, in the `clusters` section.

## Example Output

tcollector passes output to WaveFront.

### WaveFront Message Fields

1. `metricName`: mind the order of significance
1. `metricValue`: actual metric
1. `timestamp`: seconds since the UNIX epoch
1. `source`: usually the source host or address
1. `pointTags`: metadata key/value pairs

```
"lb.vs.vs_sjetest_8443.clientside_tot-conns" 7629951 1492449271 10.22.245.25 lb="hangar18"
"lb.vs.vs_sjetest_8443.clientside_bits-out" 4407439639352 1492449271 10.22.245.25 lb="hangar18"
"lb.vs.vs_sjetest_8443.clientside_bits-in" 312275341032 1492449271 10.22.245.25 lb="hangar18"
"lb.vs.vs_sjetest_8443.clientside_cur-conns" 9709 1492449271 10.22.245.25 lb="hangar18"
```

## To Do

* More metrics: pool, node, snat, etc
* Incorporate information from list commands
* Include Docker container deployment instructions
