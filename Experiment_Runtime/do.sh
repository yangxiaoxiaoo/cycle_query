#/bin/bash


mkdir -p plots/TwitterCycles/
hash=$(mktemp -d)
echo "500 600 700" > ${hash}/3
echo "300 400 500" > ${hash}/4
echo "100 200 300" > ${hash}/5
echo "50 100 150" > ${hash}/7
for l in 4 5 7
do
	value=$(< ${hash}/$l)
	IFS=' ' read -ra maxids <<< $value
	for maxid in "${maxids[@]}"
	do
		python run.py -i batch_ranking anyk_sort anyk_lazy anyk_lazysort -pq Heap -dataset Twitter -query Cycle -l $l -mid $maxid
		suff="_Heap_Twitter_Cycle_l${l}_m${maxid}.out"
		python plot.py -i "anyk_sort${suff}" "anyk_lazy${suff}" "anyk_lazysort${suff}" -b "batch_ranking${suff}" -l "anyk_sort" "anyk_lazy" "batch_ranking"\
				-o "plots/TwitterCycles/l${l}_m${maxid}" -t "Twitter dataset, l=$l, max_id=$maxid" -x "Time(sec)" -y "k"
	done
done


: '
mkdir -p plots/RandomPaths/
hash=$(mktemp -d)
echo "500 600 700" > ${hash}/3
echo "100 200 300" > ${hash}/5
echo "50 100 150" > ${hash}/7
for l in 3 5 7
do
	value=$(< ${hash}/$l)
	IFS=' ' read -ra ns <<< $value
	for n in "${ns[@]}"
	do
		echo "$n $(echo "$n" | awk '{print $1/2}') $(echo "$n" | awk '{print sqrt($1)}') $(echo "$n" | awk '{print sqrt($1)/2}')" > ${hash}/$l_$n
		echo "$n $(echo "$n" | awk '{print $1/2}') $(echo "$n" | awk '{print sqrt($1)}') $(echo "$n" | awk '{print sqrt($1)/2}')"
	done	
done


for l in 3 5 7
do
	value=$(< ${hash}/$l)
	IFS=' ' read -ra ns <<< $value
	for n in "${ns[@]}"
	do
		python run.py -i batch_ranking anyk_sort anyk_lazy -pq Heap -dataset Random -query Path -l $l -n $n -delta $n
		suff="_Heap_Random_Path_l${l}_n${n}_d${n}.out"
		python plot.py -i "anyk_sort${suff}" "anyk_lazy${suff}" -b "batch_ranking${suff}" -l "anyk_sort" "anyk_lazy" "batch_ranking"\
				-o "plots/RandomPaths/l${l}_n${n}_d${n}" -t "Random dataset, l=$l, n=$n, Delta=${n}" -x "Time(sec)" -y "k"
	done
done
'