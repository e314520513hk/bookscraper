import datetime

def err_log(msg):
    format = '%(asctime)s - %(message)s' %{
        "asctime":datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
        "message":msg
        }    

    with open("errlog.txt", 'a') as errlog:
  
        errlog.write(format+"\n")

def test_log(msg):

    format = '%(asctime)s - %(message)s' %{
        "asctime":datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S"),
        "message":msg
        }    

    with open("testlog.txt", 'a') as errlog:
  
        errlog.write(format+"\n")