#!/usr/bin/env python

print("Select one of the following options using a number q for exit")
print("1. Create policy")
print("2. Update policy")
print("3. Cancel policy")
print("4. Make payment")
print("5. Consult balance")
print("q Quit program")
options = raw_input("Select an option ")
if options == "1":
    print("you selected policy creation")
elif options == "2":
    print("you selected policy update")
elif options == "3":
    print("you selected policy cancelation")
elif options == "4":
    print("you selected policy payment")
elif options == "5":
    print("you selected policy balance")
elif options == "q":
    print("Bye")
    quit
else:
    print("invalid option")
    quit
