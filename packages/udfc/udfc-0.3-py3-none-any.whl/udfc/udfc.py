import os
def main():
    version = 0.3
    Entry = {}
    # essential stuff
    Entry['Name'] = input("Enter the name: ")
    Entry['Exec'] = input("Enter the program path: ")
    Entry['Comment'] = input("Enter a comment: ")
    if Entry['Comment'] == '':
        Entry['Comment'] = None
    Entry['Workdir'] = input("Enter the working directory (leave empty if unknown): ")
    Entry['Version'] = input("Enter the program's version: ")
    # ask if program should be ran in a terminal
    while True:
        Entry['Terminal'] = input("Do you want to open the program in a terminal? [Y/n] ")
        if Entry['Terminal'] in ['n', 'N']:
            Entry['Terminal'] = False
            break
        elif Entry['Terminal'] in ['y', 'Y']:
            Entry['Terminal'] = True
            break
        else:
            print("Invalid response")
            continue
    # ask for the program type
    print("Available program types:")
    types = ['Link', 'Application', 'Directory']
    for i in types:
        print(i)
    print("")
    while True:
        Entry['Type'] = input("Enter one of the listed Types: ")
        if Entry['Type'] not in types:
            continue
        else:
            break
    while True:
        # ask where to write the output
        WillInstall = input("Do you want to install the file? [Y/n] ")
        if WillInstall in ['Y', 'y']:
            os.makedirs(f'{os.path.expanduser('~')}/.local/share/applications', exist_ok=True)
            with open(f'{os.path.expanduser('~')}/.local/share/applications/{Entry['Name']}.desktop', 'w') as entry:
                entry.write('[Desktop Entry]\n')
                entry.write(f'Type={Entry['Type']}\n')
                entry.write(f"Version={Entry['Version']}\n")
                entry.write(f"Name={Entry['Name']}\n")
                entry.write(f"Path={Entry['Workdir']}\n")
                entry.write(f"Exec={Entry['Exec']}\n")
                entry.write(f"Terminal={Entry['Terminal']}\n")
            break
        elif WillInstall in ['N', 'n']:
                print('[Desktop Entry] ')
                print(f'Type={Entry['Type']} ')
                print(f"Version={Entry['Version']} ")
                print(f"Name={Entry['Name']} ")
                print(f"Path={Entry['Workdir']} ")
                print(f"Exec={Entry['Exec']} ")
                print(f"Terminal={Entry['Terminal']} ")
                break
        else:
            continue

    
if __name__ == "__main__":
    main()