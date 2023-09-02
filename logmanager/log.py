import datetime

def err_log(msg):
    format = '%(asctime)s - %(message)s' %{
        "asctime":datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
        "message":msg
        }    

    with open("log/errlog.txt", 'a') as errlog:
  
        errlog.write(format+"\n")

def test_log(msg):

    format = '%(asctime)s - %(message)s' %{
        "asctime":datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
        "message":msg
        }    

    with open("log/testlog.txt", 'a') as errlog:
  
        errlog.write(format+"\n")

def isbn_fail_log(msg,ymdhis):
    with open(f"log/isbn_fail_{ymdhis}.txt", 'a') as errlog:
  
        errlog.write(msg+"\n")