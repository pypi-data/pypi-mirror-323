#!/bin/bash

uploaded_list=("6324188c9572f29be662725f_1.jpg" "632417e09572f29be662725d_1.png")
let i=0
for file in "${uploaded_list[@]}"; do
    ((i++))
    rm $file
done

echo "deleted - $i"