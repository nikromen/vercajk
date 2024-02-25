#!/bin/bash

output=$(sensors | grep fan | awk '{print $2}')
for number in $output; do
    total=$((total + number))
    count=$((count + 1))
done

avg=$((total / count))
echo "{\"text\": \"${avg}\"}"
