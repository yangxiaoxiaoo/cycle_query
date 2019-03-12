#/bin/bash

python plot.py -ib "anyk_max_Btree_bounded" "anyk_max_Treap_bounded" -iu "anyk_max_Btree_unbounded" "anyk_max_Treap_unbounded" "anyk_max_Heap_unbounded" -b \
				-o "plots/anyk_max" -t "Any-k max ranked list implementations, Cycle Query, n=200, l=5" -x "Time (sec)" -y "k"

python plot.py -ib "anyk_sort_Btree_bounded" "anyk_sort_Treap_bounded" -iu "anyk_sort_Btree_unbounded" "anyk_sort_Treap_unbounded" "anyk_sort_Heap_unbounded" -b \
				-o "plots/anyk_sort" -t "Any-k sort ranked list implementations, Cycle Query, n=200, l=5" -x "Time (sec)" -y "k"
