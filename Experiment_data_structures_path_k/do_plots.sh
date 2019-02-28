#/bin/bash

python plot.py -ib "anyk_max_Btree_bounded" "anyk_max_Treap_bounded" -iu "anyk_max_Btree_unbounded" "anyk_max_Treap_unbounded" "anyk_max_PQ_unbounded" -b \
				-o "plots/anyk_max" -t "Any-k max ranked list implementations, Path Query, n=50, l=5" -x "Time/Sec" -y "k"

python plot.py -ib "anyk_sort_Btree_bounded" "anyk_sort_Treap_bounded" -iu "anyk_sort_Btree_unbounded" "anyk_sort_Treap_unbounded" "anyk_sort_PQ_unbounded" -b \
				-o "plots/anyk_sort" -t "Any-k sort ranked list implementations, Path Query, n=50, l=5" -x "Time/Sec" -y "k"

python plot.py -ib "HRJN_PQ_unbounded" "HRJN_Btree_bounded" "anyk_max_Btree_bounded" "anyk_sort_Btree_bounded" \
				-iu "anyk_max_Btree_unbounded" "anyk_max_PQ_unbounded" "anyk_sort_Btree_unbounded" "anyk_sort_PQ_unbounded" -b \
				-o "plots/all" -t 'Overall comparison of ranked list implementations, Path Query, n=50, l=5' -x "Time/Sec" -y "k"

python plot.py -ib "HRJN_PQ_unbounded" "HRJN_Btree_unbounded" "HRJN_Treap_unbounded" "HRJN_Btree_bounded" "HRJN_Treap_bounded" -b \
				-o "plots/hrjn" -t 'HRJN* ranked list implementations, Path Query, n=50, l=5' -x "Time/Sec" -y "k"
