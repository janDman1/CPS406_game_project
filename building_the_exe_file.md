I just ran `auto-py-to-exe` on the command line and I have the UI for using pyinstaller.
Selected the main.py by browsing to the right script location.
Then the --one-file option.
givig me this code below:

```bash
pyinstaller --noconfirm --onefile --console  "C:\_FILES_\Sync\semester-4_Winter2025\2025 CCPS 406 - Introduction to Software Engineering\CCPS406_Project\main.py"
```

Lastly get a copy of the data.txt file on the same directory for the .exe file


This is the same one but with added icon and the --clean option
```bash
pyinstaller --noconfirm --onefile --console --icon "C:\_FILES_\Sync\semester-4_Winter2025\2025 CCPS 406 - Introduction to Software Engineering\CCPS406_Project\assets\Game_logo.ico" --name "Return_Offer_Rush" --clean  "C:\_FILES_\Sync\semester-4_Winter2025\2025 CCPS 406 - Introduction to Software Engineering\CCPS406_Project\main.py"
```