from portableDB import DATABASE

DTB = DATABASE('db.db') #Name
DTB.LogType('COLORFUL') #'BASE' - just normal cmd, 'NONE' - no comments when working
DTB.CreateDatabase() #No comments

DTB.WriteDatabase(['String value', 32], 'LOL') #[] - here should be your values, 'LOL' - cell (can be any type and value)

DTB.WriteIndex('LOL!!!', 'LOL', 1) #'PON' - information, 'LOL' - cell (can be any type and value), 0 - index (only int)

print(DTB.ReadDatabase('LOL', 0)) #'LOL' - cell (can be any type and value), 'ALL' - index of array ('ALL' or any index of value in array, this argument can be ignored, in this case it will work like 'ALL' was given)

DTB.RenameDatabase('dababa') #'dababa' - New DB name

# DTB.DeleteDatabase() #No comments

