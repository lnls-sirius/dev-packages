#!/bin/bash
while IFS='' read -r line || [[ -n "$line" ]]; do
  kill -9 $line
done < "logs/ioc_pids.txt"

# Clear file
> logs/ioc_pids.txt
