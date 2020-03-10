# KatzKatz

KatzKatz is a python3 tool to parse text files containing output from Mimikatz sekurlsa::logonpasswords module.
When performing an internal network pentest sometimes you found yourself gathering many lsass.exe process dumps, 
open them using Mimikatz in order to extract clear text passwords and\or NTLM password hashes. 
Once you getter many of those (and usually some of them contain many credential sets) it becomes a bit cumbersome
to track and understand which users you compromised. KatzKatz will parse those for you and will output a CSV file 
containing only valid* sets so you can filter more easily and get the ones you need.
## Specific features
The tool will only parse valid* sets of credentials and will omit the 'null' ones.
In addition, it will compare the output and will save only unique sets of credentials.

*I'm not sure if 'valid' is the right word, KatzKatz will save results that containing at least username + password and\or NTLM password hash.

## How to use it
First, install the needed dependencies:
```
pip3 install -r requirements.txt
```
Second, run the tool with the needed flags:
```
python3 KatzKatz.py -f [FILENAME]
```

## Options to consider
* -f\-F
  * single file or folder containing text files
* -o
 * output file name (csv)
 
### Compatibility
This was tested with python 3.4 and Mimikatz 2.0+ version

### Example
Using the script on a folder containing multiple text and dmp files:
![Sample](https://github.com/xFreed0m/KatzKatz/blob/master/sample.png)

### Credit
I got a lot of ideas from MWR Labs - https://github.com/stufus/parse-mimikatz-log
And of course, https://github.com/gentilkiwi/mimikatz is one of the most amazing and used tools.

### Issues, bugs and other code-issues
Yeah, I know, this code isn't the best. I'm fine with it as I'm not a developer and this is part of my learning process.
If there is an option to do some of it better, please, let me know.

_Not how many, but where._
