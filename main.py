import ftplib
import csv
import datetime
import os

# ftp_info[0] = FTP Server URL
# ftp_info[1] = FTP Server Port
# ftp_info[2] = FTP Server ID
# ftp_info[3] = FTP Server Password
# ftp_info[4] = PAN ID
# ftp_info[5] = Date

f = open('info_data/info_data.txt', 'r')
ftp_info = f.read().splitlines()
f.close()

for i in ftp_info:
    print(i)

dir_name = '/local/inspection/' + str(ftp_info[4]) + '/data/' + str(ftp_info[5])
ftp=ftplib.FTP()
ftp.connect(ftp_info[0], int(ftp_info[1]))
ftp.login(ftp_info[2],ftp_info[3])
ftp.cwd(dir_name)
x = ftp.nlst()
ftp.close()

write_list = []
data_check = []
detect_count = 1

for num in range(1, 100):
    check_str = '_' + str(num) + '.csv'
    check_list = []
    for i in x:
        if check_str in i:
            check_list.append(i.split('_')[2])
            if detect_count == int(i.split('_')[2]):
                write_list.append([datetime.datetime.strptime(i.split('_')[1], '%Y%m%d%H%M%S') ,i.split('_')[2]])
                detect_count = detect_count + 1
    data_check.append(check_list)


for i in data_check:
    check_count = 1
    for j in i:
        write_list.append([])
        while(check_count != int(j)):
            write_list[check_count-1].append('x')
            check_count = check_count + 1
        write_list[check_count-1].append('o')
        check_count = check_count + 1
write_list = list(filter(None, write_list))
print(write_list)

f = open(str(datetime.datetime.now().date()) + '_' + str(ftp_info[4]) + '.csv', 'w', newline='')
csvwr = csv.writer(f)
csvwr.writerow(['date', 'No.', 'M', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10'])
for i in write_list:
    csvwr.writerow(i)
f.close()

# fd = open("./" + filename,'wb')
# ftp.retrbinary("RETR " + filename, fd.write)
# fd.close()