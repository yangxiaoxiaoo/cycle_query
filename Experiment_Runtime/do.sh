#/bin/bash

mkdir -p plots/RandomCycles/
hash=$(mktemp -d)
echo "1000 1250 1500" > ${hash}/3
echo "250 500 750" > ${hash}/5
echo "50 75 100" > ${hash}/7
for l in 3 5 7
do
	value=$(< ${hash}/$l)
	IFS=' ' read -ra ns <<< $value
	for n in "${ns[@]}"
	do
		for delta in "$n" "$(echo "$n" | awk '{print int($1/2)}')" "$(echo "$n" | awk '{print int(sqrt($1))}')" "$(echo "$n" | awk '{print int(sqrt($1)/2)}')" #n n/2 sqrt(n) sqrt(n/2)
		do
			python generate_data.py -dataset Random -query Cycle -l $l -n $n -delta $delta
			for impl in batch_ranking anyk_sort anyk_lazy anyk_lazysort
			do
				for pq in Heap
				do
					python run.py -i $impl -pq $pq -dataset Random -query Cycle -l $l -n $n -delta $delta
				done
			done
			suff="_Heap_Random_Cycle_l${l}_n${n}_d${delta}.out"
			python plot.py -i "anyk_sort${suff}" "anyk_lazy${suff}" "anyk_lazysort${suff}" -b "batch_ranking${suff}" -l "anyk_sort" "anyk_lazy" "anyk_lazysort" "batch_ranking"\
					-o "plots/RandomCycles/l${l}_n${n}_d${delta}" -t "Random dataset, Cycle, l=$l, n=$n, Delta=${delta}" -x "Time(sec)" -y "k"
		done
	done	
done


mkdir -p plots/TwitterCycles/
hash=$(mktemp -d)
echo "500 750 1000" > ${hash}/3
echo "250 350 450" > ${hash}/5
echo "150 200 250" > ${hash}/7
for l in 3 5 7
do
	value=$(< ${hash}/$l)
	IFS=' ' read -ra maxids <<< $value
	for maxid in "${maxids[@]}"
	do
		python generate_data.py -dataset Twitter -query Cycle -l $l -mid $maxid
		for impl in batch_ranking anyk_sort anyk_lazy anyk_lazysort
		do
			for pq in Heap
			do
				python run.py -i $impl -pq $pq -dataset Twitter -query Cycle -l $l -mid $maxid
			done
		done

		suff="_Heap_Twitter_Cycle_l${l}_m${maxid}.out"
		python plot.py -i "anyk_sort${suff}" "anyk_lazy${suff}" "anyk_lazysort${suff}" -b "batch_ranking${suff}" -l "anyk_sort" "anyk_lazy" "anyk_lazysort" "batch_ranking"\
				-o "plots/TwitterCycles/l${l}_m${maxid}" -t "Twitter dataset, Cycle, l=$l, max_id=$maxid" -x "Time(sec)" -y "k"
	done
done


mkdir -p plots/RandomPaths/
hash=$(mktemp -d)
echo "500 750 1000" > ${hash}/3
echo "100 200 300" > ${hash}/5
echo "50 100 150" > ${hash}/7
for l in 3 5 7
do
	value=$(< ${hash}/$l)
	IFS=' ' read -ra ns <<< $value
	for n in "${ns[@]}"
	do
		for delta in "$n" "$(echo "$n" | awk '{print int($1/2)}')" "$(echo "$n" | awk '{print int(sqrt($1))}')" "$(echo "$n" | awk '{print int(sqrt($1)/2)}')" #n n/2 sqrt(n) sqrt(n/2)
		do
			python generate_data.py -dataset Random -query Path -l $l -n $n -delta $delta
			for impl in batch_ranking anyk_sort anyk_lazy anyk_lazysort
			do
				for pq in Heap
				do
					python run.py -i $impl -pq $pq -dataset Random -query Path -l $l -n $n -delta $delta
				done
			done
			suff="_Heap_Random_Path_l${l}_n${n}_d${delta}.out"
			python plot.py -i "anyk_sort${suff}" "anyk_lazy${suff}" "anyk_lazysort${suff}" -b "batch_ranking${suff}" -l "anyk_sort" "anyk_lazy" "anyk_lazysort" "batch_ranking"\
					-o "plots/RandomPaths/l${l}_n${n}_d${delta}" -t "Random dataset, Path, l=$l, n=$n, Delta=${delta}" -x "Time(sec)" -y "k"
		done
	done	
done
