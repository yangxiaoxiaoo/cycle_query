#/bin/bash

mkdir -p plots/TwitterPaths/
hash=$(mktemp -d)
echo "250 350 450" > ${hash}/3
echo "150 200 250" > ${hash}/5
for l in 3 5
do
	value=$(< ${hash}/$l)
	IFS=' ' read -ra maxids <<< $value
	for maxid in "${maxids[@]}"
	do
		python generate_data.py -dataset Twitter -query Path -l $l -mid $maxid
		for impl in batch_ranking anyk_sort anyk_lazy anyk_lazysort
		do
			for pq in Heap
			do
				python run.py -i $impl -pq $pq -dataset Twitter -query Path -l $l -mid $maxid
			done
		done

		suff="_Heap_Twitter_Path_l${l}_m${maxid}.out"
		python plot.py -i "anyk_sort${suff}" "anyk_lazy${suff}" "anyk_lazysort${suff}" -b "batch_ranking${suff}" -l "anyk_sort" "anyk_lazy" "anyk_lazysort" "batch_ranking"\
				-o "plots/TwitterPaths/l${l}_m${maxid}" -t "Twitter dataset, Path, l=$l, max_id=$maxid" -x "Time(sec)" -y "k"
	done
done