##1. 
Normally, ls shows only the names of files and directories. But the -l option of the ls command displays them in long listing format. 
The output contains information such as file type, permissions, owner, group, number of links, size, date and time, and file name.
For example, the first 10 characters of a line may look like:
drwxr-xr-x
The first character represents the file type. Here, d means it is a directory. If the first character is -, it means it is a regular file, and if it is l, 
it means it is a symbolic link.
The remaining 9 characters represent the permissions:
Here, rwx means the owner has permission to read, write, and execute. The first r-x means the group has permission to read and execute, but cannot write. 
The second r-x means others also have permission to read and execute, but cannot write.
Therefore, drwxr-xr-x means it is a directory, where the owner can read, write, and execute, while the group and others can read and execute but cannot write.

##2. 
A glob is a pattern used by the shell to match file names. It helps us select multiple files without typing each file name separately.

the *.zip is a glob pattern. Here, * means any number of characters, so *.zip matches all files whose names end with .zip.

After creating a test directory with some file the output for ls *.txt is:
(base)  mithesh@Mitheshs-MacBook-Air-3421 globtest % ls *.txt
a.txt		b.txt		c.txt		file1.txt	file10.txt	file2.txt


The output for ls file?.txt is:
 mithesh@Mitheshs-MacBook-Air-3421 globtest % ls file?.txt
file1.txt	file2.txt
? represents exactly one character.

The output for ls {a,b,c}.txt is:
(base) mithesh@Mitheshs-MacBook-Air-3421 globtest % ls {a,b,c}.txt
a.txt	b.txt	c.txt

Therefore, a glob is a shell pattern used for matching file names, where * matches any number of characters and ? matches one character.

##3.
There are three different types of quotes commonly used in the shell: single quotes ' ', double quotes " ", and ANSI-C quotes $' '.

Single quotes
Single quotes preserve the contents exactly as they are. Variables and special characters are not expanded.
For example:
echo '$HOME'
Output:
$HOME
Here, $HOME is printed as it is instead of showing the value of the HOME variable.

Double quotes
Double quotes allow variables to be expanded, but they generally prevent unwanted word splitting and glob expansion.
For example:
echo "$HOME"
It displays the actual home directory, such as:
/Users/ricky

ANSI-C quotes
ANSI-C quotes use $'...' and allow escape sequences such as \n for a newline.
For example:
printf '%s\n' $'Price: \$100\nHello!'
Output:
Price: $100
Hello!
Here, \$ represents a literal $ and \n represents a newline. The ! is also included as a normal character.
Therefore, single quotes treat everything literally, double quotes allow variable expansion, and ANSI-C quotes allow escape sequences such as \n.


##4.
The shell has three standard streams:
stdin (0)
stdout (1)
stderr (2)
stdin is the standard input, stdout is the standard output, and stderr is the standard error output.

Run:
ls /nonexistent /tmp
Since /nonexistent does not exist, an error message is produced. At the same time, the contents of /tmp are displayed.
We can redirect stdout to one file and stderr to another file using:
ls /nonexistent /tmp > output.txt 2> error.txt
Here:
1> output.txt
redirects stdout to output.txt.
And:
2> error.txt
redirects stderr to error.txt.
To redirect both stdout and stderr to the same file, we can use:
ls /nonexistent /tmp > all.txt 2>&1
Here, 2>&1 means that stderr (2) is redirected to the same location as stdout (1).
Therefore, both the normal output and error messages will be stored in all.txt.

##5. 
$? stores the exit status of the last executed command. An exit status of 0 normally means the command was successful, while a non-zero value means that the command failed.

For example:
true
echo $?
Output:
0
The && operator runs the next command only if the previous command succeeds.
For example:
mkdir test && echo "Directory created"
The echo command runs only if mkdir succeeds.

The || operator runs the next command only if the previous command fails.
To create /tmp/mydir only if it does not already exist, we can use:
[ -d /tmp/mydir ] || mkdir /tmp/mydir
Here, [ -d /tmp/mydir ] checks whether /tmp/mydir is already a directory.
If the directory exists, the test succeeds and mkdir is not executed.
If the directory does not exist, the test fails and because of ||, the following command:
mkdir /tmp/mydir
is executed.
Therefore, this one-liner creates the directory only when it does not already exist.

##6.
cd has to be built into the shell because it changes the current working directory of the shell itself. 
If cd were a standalone program, it would run as a separate process and could only change the directory of that process. 
After the program finishes, the shell would remain in its original directory. 
Therefore, cd must be a shell builtin so that it can change the working directory of the current shell.



##7.
We need to write a shell script that takes a filename as the first argument ($1) and checks whether the file exists using [ -f ... ].
Step 1: Create the script
Run:
nano check.sh
Write the following code inside the file:
#!/bin/bash

if [ -f "$1" ]
then
    echo "File exists: $1"
else
    echo "File does not exist: $1"
fi
Here, $1 represents the first argument passed to the script.
For example:
./check.sh test.txt
Here:
$1 = test.txt

The condition:
[ -f "$1" ]
checks whether the given file exists and is a regular file.

Step 2: Try running the script
First save the file and then run:
./check.sh test.txt
You will most likely get:
zsh: permission denied: ./check.sh
This happens because the script does not have execute permission yet.

Step 3: Give execute permission
Run:
chmod +x check.sh
Here, chmod is used to change file permissions and +x means add execute permission.
Now run:
./check.sh test.txt
If test.txt does not exist, the output will be:
File does not exist: test.txt

Step 4: Create the file and test again
Create the file:
touch test.txt
Now run:
./check.sh test.txt
Output:
File exists: test.txt

Why is chmod +x necessary?
Normally, when we create a script, it does not automatically have execute permission. Therefore, trying to run it directly using:
./check.sh test.txt
gives a permission denied error.
The command:
chmod +x check.sh
adds execute permission to the script, allowing the operating system to run it directly.


##8. 
We can use the cp command along with the date command to copy a file and add today's date to the filename.
For example, if the original file is:
notes.txt
we can use the following command:
cp notes.txt "notes_$(date +%Y-%m-%d).txt"
Here, cp is used to copy the file.
The command:
date +%Y-%m-%d
gives today's date in the format:
YYYY-MM-DD
For example, 
(base) mithesh@Mitheshs-MacBook-Air-3421 ~ % touch notes.txt
(base) mithesh@Mitheshs-MacBook-Air-3421 ~ % ls notes.txt
notes.txt
(base) mithesh@Mitheshs-MacBook-Air-3421 ~ % cp notes.txt "notes_$(date +%Y-%m-%d).txt"
(base) mithesh@Mitheshs-MacBook-Air-3421 ~ % ls
a.txt			Downloads		Movies			notes.txt
Desktop			globtest		Music			Pictures
Documents		Library			notes_2026-08-20.txt	Public
Therefore, the command automatically copies notes.txt to a backup file containing today's date in its filename.

##9.
to find the 5 most common file extensions we use the command :

find . -type f | awk -F. 'NF>1 {print $NF}' | sort | uniq -c | sort -nr | head -5
```

Here:

* `find . -type f` → finds all files.
* `awk -F.` → gets the file extension.
* `sort` → sorts the extensions.
* `uniq -c` → counts how many times each extension occurs.
* `sort -nr` → sorts from highest count to lowest.
* `head -5` → shows only the top 5.

Example output:

```text
15 txt
10 c
8 pdf
5 jpg
3 sh
```

##10.
command:
find . -type f -name "*.sh" -print0 | xargs -0 wc -l


Here:

* `find . -type f -name "*.sh"` → finds all `.sh` files.
* `-print0` → safely passes filenames to `xargs`, even if they contain spaces.
* `xargs -0` → converts the filenames into arguments for the next command.
* `wc -l` → counts the number of lines in each file.

output:
mithesh@Mitheshs-MacBook-Air-3421 ~ % find . -type f -name "*.sh" -print0 | xargs -0 wc -l
find: ./Library/Application Support/MobileSync: Operation not permitted
find: ./Library/Application Support/CallHistoryTransactions: Operation not permitted
find: ./Library/Application Support/CloudDocs: Operation not permitted
find: ./Library/Application Support/com.apple.sharedfilelist: Operation not permitted
find: ./Library/Application Support/Knowledge: Operation not permitted
find: ./Library/Application Support/com.apple.TCC: Operation not permitted
find: ./Library/Application Support/FileProvider: Operation not permitted
find: ./Library/Application Support/AddressBook: Operation not permitted
find: ./Library/Application Support/FaceTime: Operation not permitted
find: ./Library/Application Support/DifferentialPrivacy: Operation not permitted
find: ./Library/Application Support/com.apple.avfoundation/Frecents: Operation not permitted
find: ./Library/Application Support/CallHistoryDB: Operation not permitted
find: ./Library/Assistant/SiriVocabulary: Operation not permitted
find: ./Library/Daemon Containers: Operation not permitted
find: ./Library/Autosave Information: Operation not permitted
find: ./Library/IdentityServices: Operation not permitted
find: ./Library/Messages: Operation not permitted
find: ./Library/HomeKit: Operation not permitted
find: ./Library/Sharing: Operation not permitted
find: ./Library/com.apple.aiml.instrumentation: Operation not permitted
find: ./Library/Mail: Operation not permitted
find: ./Library/Trial: Operation not permitted
find: ./Library/AppleMediaServices: Operation not permitted
find: ./Library/DuetExpertCenter: Operation not permitted
find: ./Library/Accounts: Operation not permitted
find: ./Library/Safari: Operation not permitted
find: ./Library/Biome: Operation not permitted
find: ./Library/IntelligencePlatform: Operation not permitted
find: ./Library/Shortcuts: Operation not permitted
find: ./Library/Suggestions: Operation not permitted
find: ./Library/Weather: Operation not permitted
find: ./Library/Group Containers/group.com.apple.stocks-news: Operation not permitted
find: ./Library/Group Containers/group.com.apple.photolibraryd.private: Operation not permitted
find: ./Library/Group Containers/group.com.apple.feedback: Operation not permitted
find: ./Library/Group Containers/group.com.apple.siri.inference: Operation not permitted
find: ./Library/Group Containers/group.com.apple.telephonyutilities.callservicesd: Operation not permitted
find: ./Library/Group Containers/group.com.apple.swtransparency: Operation not permitted
find: ./Library/Group Containers/group.com.apple.coreservices.useractivityd: Operation not permitted
find: ./Library/Group Containers/group.com.apple.ArchiveUtility.PKSignedContainer: Operation not permitted
find: ./Library/Group Containers/group.com.apple.accessibility.voicebanking: Operation not permitted
find: ./Library/Group Containers/group.com.apple.icloud.searchpartyuseragent: Operation not permitted
find: ./Library/Group Containers/group.com.apple.siri.referenceResolution: Operation not permitted
find: ./Library/Group Containers/group.com.apple.stocks: Operation not permitted
find: ./Library/Group Containers/group.com.apple.usernoted: Operation not permitted
find: ./Library/Group Containers/group.com.apple.VoiceMemos.shared: Operation not permitted
find: ./Library/Group Containers/group.com.apple.contacts: Operation not permitted
find: ./Library/Group Containers/group.com.apple.secure-control-center-preferences: Operation not permitted
find: ./Library/Group Containers/group.com.apple.chronod: Operation not permitted
find: ./Library/Group Containers/com.apple.MailPersonaStorage: Operation not permitted
find: ./Library/Group Containers/group.com.apple.private.translation: Operation not permitted
find: ./Library/Group Containers/group.com.apple.appstoreagent: Operation not permitted
find: ./Library/Group Containers/group.com.apple.portrait.BackgroundReplacement: Operation not permitted
find: ./Library/Group Containers/group.com.apple.icloud.fmfcore: Operation not permitted
find: ./Library/Group Containers/group.com.apple.liveactivitiesd: Operation not permitted
find: ./Library/Group Containers/group.com.apple.amsondevicestoraged: Operation not permitted
find: ./Library/Group Containers/group.com.apple.SiriTTS: Operation not permitted
find: ./Library/Group Containers/group.com.apple.notes.import: Operation not permitted
find: ./Library/Group Containers/group.com.apple.calendar: Operation not permitted
find: ./Library/Group Containers/group.com.apple.siri.userfeedbacklearning: Operation not permitted
find: ./Library/Group Containers/group.com.apple.gamecenter: Operation not permitted
find: ./Library/Group Containers/group.com.apple.tips: Operation not permitted
find: ./Library/Group Containers/group.com.apple.tv.sharedcontainer: Operation not permitted
find: ./Library/Group Containers/group.com.apple.loginwindow.persistent-apps: Operation not permitted
find: ./Library/Group Containers/group.com.apple.spotlight: Operation not permitted
find: ./Library/Group Containers/group.com.apple.studentd: Operation not permitted
find: ./Library/Group Containers/group.com.apple.ManagedSettings: Operation not permitted
find: ./Library/Group Containers/group.com.apple.sharingd: Operation not permitted
find: ./Library/Group Containers/group.com.apple.printtool: Operation not permitted
find: ./Library/Group Containers/group.com.apple.corerepair: Operation not permitted
find: ./Library/Group Containers/group.com.apple.news: Operation not permitted
find: ./Library/Group Containers/group.com.apple.mobileslideshow.PhotosFileProvider: Operation not permitted
find: ./Library/Group Containers/group.com.apple.scopedbookmarkagent: Operation not permitted
find: ./Library/Group Containers/group.com.apple.weather: Operation not permitted
find: ./Library/Group Containers/com.apple.systempreferences.cache: Operation not permitted
find: ./Library/Group Containers/group.com.apple.feedbacklogger: Operation not permitted
find: ./Library/Group Containers/group.com.apple.controlcenter: Operation not permitted
find: ./Library/Group Containers/group.com.apple.siri.remembers: Operation not permitted
find: ./Library/Group Containers/group.com.apple.notes: Operation not permitted
find: ./Library/Group Containers/com.apple.stickersd.group: Operation not permitted
find: ./Library/Group Containers/group.com.apple.UserNotifications: Operation not permitted
find: ./Library/Group Containers/group.com.apple.tipsnext: Operation not permitted
find: ./Library/Group Containers/group.com.apple.moments: Operation not permitted
find: ./Library/Group Containers/group.com.apple.Safari.SandboxBroker: Operation not permitted
find: ./Library/Group Containers/group.com.apple.transparency: Operation not permitted
find: ./Library/Group Containers/group.com.apple.webkit.webpushd: Operation not permitted
find: ./Library/Group Containers/group.com.apple.reminders: Operation not permitted
find: ./Library/Group Containers/group.com.apple.findmy.findmylocateagent: Operation not permitted
find: ./Library/Group Containers/group.com.apple.mail: Operation not permitted
find: ./Library/Group Containers/com.apple.bird: Operation not permitted
find: ./Library/Group Containers/group.com.apple.DeviceActivity: Operation not permitted
find: ./Library/Group Containers/group.com.apple.Journal: Operation not permitted
find: ./Library/Group Containers/com.apple.Home.group: Operation not permitted
find: ./Library/Group Containers/group.com.apple.iCloudDrive: Operation not permitted
find: ./Library/Group Containers/group.com.apple.FaceTime: Operation not permitted
find: ./Library/Group Containers/group.com.apple.energykit: Operation not permitted
find: ./Library/Group Containers/com.apple.PreviewLegacySignaturesConversion: Operation not permitted
find: ./Library/Group Containers/group.com.apple.siri.ASR.shared: Operation not permitted
find: ./Library/Group Containers/group.com.apple.replicatord: Operation not permitted
find: ./Library/Group Containers/group.com.apple.Photos.PhotosFileProvider: Operation not permitted
find: ./Library/Group Containers/group.com.apple.icloud.fmipcore: Operation not permitted
find: ./Library/Group Containers/group.com.apple.AppleSpell: Operation not permitted
find: ./Library/Group Containers/group.com.apple.mlhost: Operation not permitted
find: ./Library/Group Containers/group.com.apple.FamilyControls: Operation not permitted
find: ./Library/Group Containers/group.com.apple.Maps: Operation not permitted
find: ./Library/Group Containers/group.com.apple.PegasusConfiguration: Operation not permitted
find: ./Library/Group Containers/group.com.apple.shortcuts: Operation not permitted
find: ./Library/Group Containers/group.com.apple.people: Operation not permitted
find: ./Library/Group Containers/com.apple.MessagesLegacyTransferArchive: Operation not permitted
find: ./Library/Containers/com.apple.VoiceMemos: Operation not permitted
find: ./Library/Containers/com.apple.archiveutility: Operation not permitted
find: ./Library/Containers/com.apple.Maps/Data/Maps: Operation not permitted
find: ./Library/Containers/com.apple.Home: Operation not permitted
find: ./Library/Containers/com.apple.Safari: Operation not permitted
find: ./Library/Containers/com.apple.mail: Operation not permitted
find: ./Library/Containers/com.apple.MobileSMS: Operation not permitted
find: ./Library/Containers/com.apple.Notes: Operation not permitted
find: ./Library/Containers/com.apple.corerecents.recentsd/Data/Library/Recents: Operation not permitted
find: ./Library/Containers/com.apple.stocks: Operation not permitted
find: ./Library/Containers/com.apple.Safari.WebApp: Operation not permitted
find: ./Library/ContainerManager: Operation not permitted
find: ./Library/PersonalizationPortrait: Operation not permitted
find: ./Library/Metadata/CoreSpotlight: Operation not permitted
find: ./Library/Metadata/com.apple.IntelligentSuggestions: Operation not permitted
find: ./Library/Cookies: Operation not permitted
find: ./Library/CoreFollowUp: Operation not permitted
find: ./Library/StatusKit: Operation not permitted
find: ./Library/DoNotDisturb: Operation not permitted
find: ./Library/Caches/familycircled: Operation not permitted
find: ./Library/Caches/com.apple.HomeKit: Operation not permitted
find: ./Library/Caches/CloudKit: Operation not permitted
find: ./Library/Caches/com.apple.Safari: Operation not permitted
find: ./Library/Caches/com.apple.containermanagerd: Operation not permitted
find: ./Library/Caches/com.apple.Safari.SafeBrowsing: Operation not permitted
find: ./Library/Caches/FamilyCircle: Operation not permitted
find: ./Library/Caches/com.apple.homed: Operation not permitted
find: ./Library/Caches/com.apple.ap.adprivacyd: Operation not permitted
find: ./.Trash: Operation not permitted
      33 ./Library/Arduino15/libraries/Firmata/release.sh
     514 ./Library/Arduino15/packages/arduino/tools/avr-gcc/7.3.0-atmel3.6.1-arduino7/libexec/gcc/avr/7.3.0/install-tools/fixinc.sh
     120 ./Library/Arduino15/packages/arduino/hardware/avr/1.8.7/firmwares/wifishield/scripts/ArduinoWifiShield_upgrade.sh
      96 ./Library/Arduino15/packages/arduino/hardware/avr/1.8.7/firmwares/wifishield/scripts/ArduinoWifiShield_upgrade_mac.sh
     162 ./.tldrc/tldr/scripts/check-errors.sh
      59 ./.tldrc/tldr/scripts/pdf/build-pdf.sh
      79 ./.tldrc/tldr/scripts/build.sh
      53 ./.tldrc/tldr/scripts/deploy.sh
     267 ./.tldrc/tldr/scripts/check-pr.sh
     145 ./.tldrc/tldr/scripts/test.sh
      14 ./.vscode/extensions/ms-python.debugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/_vendored/pydevd/pydevd_attach_to_process/linux_and_mac/compile_mac.sh
      11 ./.vscode/extensions/ms-python.debugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/_vendored/pydevd/pydevd_attach_to_process/linux_and_mac/compile_linux.sh
     484 ./Downloads/Visual Studio Code.app/Contents/Resources/app/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh
      39 ./Downloads/Visual Studio Code.app/Contents/Resources/app/out/vs/base/node/ps.sh
      13 ./Downloads/Visual Studio Code.app/Contents/Resources/app/out/vs/base/node/terminateProcess.sh
      64 ./Downloads/Visual Studio Code.app/Contents/Resources/app/out/vs/base/node/cpuUsage.sh
      66 ./Downloads/Visual Studio Code.app/Contents/Resources/app/node_modules/jschardet/scripts/run-workflow.sh
      67 ./Downloads/Visual Studio Code.app/Contents/Resources/app/node_modules/jschardet/scripts/show-size-changes.sh
      13 ./Downloads/Visual Studio Code.app/Contents/Resources/app/extensions/ms-vscode.js-debug/src/targets/node/terminateProcess.sh
       1 ./Downloads/Visual Studio Code.app/Contents/Resources/app/extensions/git/dist/askpass-empty.sh
       1 ./Downloads/Visual Studio Code.app/Contents/Resources/app/extensions/git/dist/git-editor-empty.sh
       4 ./Downloads/Visual Studio Code.app/Contents/Resources/app/extensions/git/dist/git-editor.sh
       5 ./Downloads/Visual Studio Code.app/Contents/Resources/app/extensions/git/dist/ssh-askpass.sh
       1 ./Downloads/Visual Studio Code.app/Contents/Resources/app/extensions/git/dist/ssh-askpass-empty.sh
       5 ./Downloads/Visual Studio Code.app/Contents/Resources/app/extensions/git/dist/askpass.sh
     484 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh
      39 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/out/vs/base/node/ps.sh
      13 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/out/vs/base/node/terminateProcess.sh
      64 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/out/vs/base/node/cpuUsage.sh
      66 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/node_modules/jschardet/scripts/run-workflow.sh
      67 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/node_modules/jschardet/scripts/show-size-changes.sh
      13 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/extensions/ms-vscode.js-debug/src/targets/node/terminateProcess.sh
       1 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/extensions/git/dist/askpass-empty.sh
       1 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/extensions/git/dist/git-editor-empty.sh
       4 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/extensions/git/dist/git-editor.sh
       5 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/extensions/git/dist/ssh-askpass.sh
       1 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/extensions/git/dist/ssh-askpass-empty.sh
       5 ./Downloads/Visual Studio Code 2.app/Contents/Resources/app/extensions/git/dist/askpass.sh
    3079 total
This means `33 ./Library/Arduino15/libraries/Firmata/release.sh` has 33 lines and there are 3079 lines in total.

## 11. 

Run:
curl -s https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json | jq -r '.[] | select(.version > 6) | .name'

Here:
curl -s → fetches the JSON data from the given URL.
| → sends the output of curl to jq.
.[] → goes through each person in the JSON data.
select(.version > 6) → selects only people whose version is greater than 6.
.name → prints only their names.
-r → prints the names as normal text without quotation marks.

mithesh@Mitheshs-MacBook-Air-3421 ~ % curl -s https://microsoftedge.github.io/Demos/json-dummy-data/64KB.json | jq -r '.[] | select(.version > 6) | .name'
Adeel Solangi
Aamir Solangi
Adil Eli
Adil Abro
Antía Sixirei
Aygul Mutellip
Celtia Anes
George Mifsud
Dialè Meso
Doreen Bartolo
Ali Ayaz
Guzelnur Polat
John Falzon
Marcos Amboade
Shafqat Memon
Meladi Papo
Sabela Veloso
Madule Ledimo
Philip Camilleri
Hunadi Makgatho
Charmaine Abela
Tumelò Letamo
Tegra Núnez
Dilnur Qeyser
Iago Peirallo
Josephine Balzan
Mmathabò Mojapelo
Kgabo Lerumo
Lawrence Scicluna
Joseph Grech
Lesetja Theko
Martiño Arxíz
Malehumò Ledwaba
Lajwanti Kumari
Maria Sammut
Matome Molamo
Noa Ervello
sayama Amir
Mariña Quintá
Memet Tursun
Rashid Rajput
Nicholas Micallef
Peter Zammit
Maname Mohlare
Tshepè Mobu
Monica Lohana
Joanne Scerri
Ratanang Maphutha
Thobile Mbele
Kristján Kristjánsson
Stefán Stefánsson
Preeti Rajdan
Sanjay Trivedi
Damir Benic
Sigrún Kristjánsdóttir
Rajesh Santoshi
Mxolisi Mhlongo
Monty Dubey
Richa Choukse
Ingibjörg Ólafsdóttir
Mogorosi Bakwena
Ronak Gupta
Chetana Hegde
Mohan Pandey
Haris Osmanovic
Kenosi Kwenaemang
Adnan Spahic
Kabelo Morwe
Einar Einarsson
Sigríður Einarsdóttir
Sonu Jain
Boitumelo Ngwako
Modise Tau
Gunnar Gunnarsson
Kgosietsile Bogatsu
Monika Nayak
Lucky Shastry
Raju Rathore
Meenakshi Benjaree
Samir Simic
Prashant Chourey
Prakash Malviya
Ivana Kalic
Denis Terzic
Bukhosi Bhengu
Siyabonga Sithole
Rohini Vasav
Sunil Kapoor
Zamokuhle Zulu

## 12.

command:
printf 'a 50 x\nb 150 y\nc 200 z\n' | awk '$2 > 100 {print $3, $2, $1}'
Here:

* `$1` → first column
* `$2` → second column
* `$3` → third column
* `$2 > 100` → prints only lines where the second column is greater than 100.
* `{print $3, $2, $1}` → swaps the first and third columns.

output:
mithesh@Mitheshs-MacBook-Air-3421 ~ % printf 'a 50 x\nb 150 y\nc 200 z\n' | awk '$2 > 100 {print $3, $2, $1}'

y 150 b
z 200 c

















