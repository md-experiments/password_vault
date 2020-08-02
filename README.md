# Password Vault
This repo is a basic password vault which allows you to encrypt some data and continuously add to it

# Usage
1. clone repo, create environment and run requirements.txt
2. Create file password.txt with your password
3. Store sensitive data in file_to_encrypt.txt
4. follow instructions in Encryption notebook to encrypt it and store to local db
5. remove/clear file_to_encrypt.txt & password.txt. Repeat 2. - 4. when you need to add new sensitive information
6. run python app.py
7. To preview ensitive data, enter password. Sensitive info will disappear after 10sec

NB: do not forget to close down browser after use as password can still be resubmitted upon page refresh