with open('soc-sign-bitcoinotc.csv', 'r') as fin:
    with open('new-bitcoinotc', 'a') as fout:
        for line in fin:
            n1, n2, rating, time = line.split(',')
            fout.write(str(n1) + ' ' + str(n2) + ' ' + str(20-int(rating)) + '\n')


