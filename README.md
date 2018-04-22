# guacamole8

## prepare

The script requires numpy, you can install it with the command

```
pip install -r pip-requirements.txt
```

## usage

```
./log_stat.py <event_file>
```

Output example:

```
Event log file name: 001.in
Backend groups involved: 2
Working time's 95th percentile: 2081998
Top 10 of the longest sending requests: 0
Requests with incomplete dataset: 0

Backend group: 0
    Total backends involved: 2
    backend0-001.yandex.ru:1963/search?
        Requests: 1
        Errors:
            Request Timeout: 1
    backend0-002.yandex.ru:1126/search?
        Requests: 1

Backend group: 1
    Total backends involved: 1
    backend1-001.yandex.ru:1085/search?
        Requests: 1```
