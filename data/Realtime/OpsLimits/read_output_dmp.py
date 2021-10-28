dmp = open('out_dmp.txt', 'r')

lines = dmp.readlines()
denied_requests_per_tau = [0 for i in range(8)]
curr_tau = -1
for line in lines:
    if(line == 'DENIED REQUEST\n'):
        denied_requests_per_tau[curr_tau] += 1
    elif(line == 'NEW_TAU\n'):
        curr_tau += 1

print(denied_requests_per_tau)
