command: vsw publish


name:create and  publish vsw package based on package.json

Description:
As a vsw user, you can create packages publish them to the vsw Repo registry for others 
to use. 


Execution Steps:
	(assuming you are using git to manage your software package code)
	1- cd ~/myproject
	2- git init
	3- git remote add origin git://git-myproject-url
	4- vsw init
	5- Respond to the prompt to modify the package.json
	6- vsw publish



Expected output:

a confirmation message indicating that my package has been successfully stored in the vsw Repo

