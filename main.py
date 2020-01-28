import ftplib
import csv
import datetime
import threading
import time

dir_raw_data = []
dir_raw_data_split = []
dir_file_name = []
dir_file_size = []
write_list = []
data_check = []
size_check = []
device_num = []
csv_header = ['date', 'No.']

f = open('info_data/info_data.txt', 'r')
ftp_info = f.read().splitlines()
f.close()

for i in ftp_info:
    print(i)

dir_name = '/local/inspection/' + str(ftp_info[4]) + '/data/' + str(ftp_info[5])
log_dir_name = '/local/inspection/' + str(ftp_info[4]) + '/log/' + str(ftp_info[5])[:-2]
command_dir_name = '/local/inspection/' + str(ftp_info[4]) + '/command'
master_log_name = ''

## Data List Download
ftp=ftplib.FTP()
ftp.connect(ftp_info[0], int(ftp_info[1]))
ftp.login(ftp_info[2],ftp_info[3])
ftp.cwd(dir_name)
ftp.dir(dir_raw_data.append)

## Log download
try:
    ftp.cwd(log_dir_name)
    x = ftp.nlst()
    for i in x:
        if str(ftp_info[5]) + '_1.txt' in i:
            master_log_name = i
    f = open(master_log_name, 'wb')
    ftp.retrbinary('RETR ' + master_log_name, f.write)
    f.close()
except (ftplib.error_perm, FileNotFoundError):
    print('No such Log File')

## Close FTP
ftp.close()

## Open Log File
try:
    f = open(master_log_name, 'r')
    log_read = f.readlines()
    f.close()

    detect_device_list = []
    for index, i in enumerate(log_read):
        if '_1.csv done.' in i:
            if 'Receive detection from enddevice' in log_read[index-1]:
                detect_device_list.append('S' + str(int(log_read[index-1].split(' ')[5]) + 1))
            else:
                detect_device_list.append('M')
except FileNotFoundError:
    print('No such Log file')

for i in dir_raw_data:
    dir_raw_data_split.append(list(filter(None, i.split(' '))))

for i in dir_raw_data_split:
    dir_file_name.append(i[8])
    dir_file_size.append(i[4])

for num in range(1, 50):
    check_str = '_' + str(num) + '.csv'
    check_list = []
    check_size_list = []
    for index, i in enumerate(dir_file_name):
        if check_str in i:
            check_list.append(i.split('_')[2])
            check_size_list.append(dir_file_size[index])
            if num in device_num:
                pass
            else:
                device_num.append(num)
    data_check.append(check_list)
    size_check.append(check_size_list)

## data min & max number check
min_num = 999
max_num = 0
data_check = list(filter(None, data_check))
for i in data_check:
    if int(min(i)) < min_num:
        min_num = int(min(i))
    if int(max(i)) > max_num:
        max_num = int(max(i))

## make write Data / time & data number
for j in range(min_num, max_num+1):
    for i in dir_file_name:
        if '_' + str(j).zfill(3) + '_' in i:
            write_list.append([datetime.datetime.strptime(i.split('_')[1], '%Y%m%d%H%M%S'), i.split('_')[2]])
            break

## Check data availability
for i_index, i in enumerate(data_check):
    check_count = min_num
    for j_index, j in enumerate(i):
        while(check_count != int(j)):
            write_list[check_count-min_num].append('0')
            check_count = check_count + 1
        if size_check[i_index][j_index] > '144000':
            write_list[check_count-min_num].append('1')
        else:
            write_list[check_count - min_num].append('!')
        check_count = check_count + 1

## detect device check
for i in range(len(write_list)):
    try:
        write_list[i].append(detect_device_list[i])
    except (IndexError, NameError):
        break

## .csv Save
save_file_name = str(datetime.datetime.now().date()) + '_' + str(ftp_info[4])
for i in device_num:
    if i == 1:
        csv_header.append('M')
    else:
        csv_header.append('S' + str(i))
f = open(save_file_name + '.csv', 'w', newline='')
csvwr = csv.writer(f)
csvwr.writerow(csv_header)
for i in write_list:
    csvwr.writerow(i)
f.close()

## make command txt
ftp=ftplib.FTP()
ftp.connect(ftp_info[0], int(ftp_info[1]))
ftp.login(ftp_info[2],ftp_info[3])
ftp.cwd(command_dir_name)

command_line = 'log\r'
make_command_file_list = []
command_state = []
for i in device_num:
    file_n = 'command' + str(i) + '.txt'
    make_command_file_list.append(file_n)
    command_state.append('True')

    f = open('command/' + file_n, 'w')
    f.write(command_line)
    f.close()

    up = open('command/' + file_n, 'rb')
    ftp.storbinary('STOR ' + file_n, up)
    up.close()

while True:
    time.sleep(10)
    x = ftp.nlst()
    print(x)
    for index, i in enumerate(make_command_file_list):
        if i in x:
            print('True')
        else:
            print('False')
            command_state[index] = 'False'
    print(command_state)
    if 'True' not in command_state:
        break

ftp.close()

## .xlsx Svae
# import openpyxl
# xl = openpyxl.Workbook()
# xl_write = xl.active
# xl_write.append(['date', 'No.', 'M', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10'])
# for i in write_list:
#     xl_write.append(i)
# xl.save(save_file_name + '.xlsx')