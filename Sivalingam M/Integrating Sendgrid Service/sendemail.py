import smtplib

def sendmail(TEXT,email):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("ananthi.r3105@gmail.com", "rzzqfkqhrvaijhmk")
    s.sendmail('ananthi.r3105@gmail.com', "1915027@nec.edu.in", 'Mail snt for checking')
    print('mail sent')