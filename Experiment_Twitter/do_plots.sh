#/bin/bash

python plot.py -iu "anyk_sort_Heap_unbounded" "anyk_max_Heap_unbounded" -b \
				-o "plots/plotSynthetic500_24" -t "Synthetic dataset, l=5, n=500, Delta=24" -x "Time(sec)" -y "k"

# Twitter dataset, l=5 ,max_id=400

# "anyk_max_PQ_unbounded" "anyk_max_Btree_unbounded" "anyk_sort_PQ_unbounded" "anyk_sort_Btree_unbounded"