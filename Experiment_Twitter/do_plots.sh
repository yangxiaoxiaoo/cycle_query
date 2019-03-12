#/bin/bash

python plot.py -iu "anyk_sort_Heap_unbounded" "anyk_sort_Btree_unbounded" -b \
				-o "plots/plot1" -t "Twitter dataset, l=5 ,max_id=500" -x "Time(sec)" -y "k"

# "anyk_max_PQ_unbounded" "anyk_max_Btree_unbounded" "anyk_sort_PQ_unbounded" "anyk_sort_Btree_unbounded"