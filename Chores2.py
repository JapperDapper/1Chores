import csv
import os
import logging
import pyperclip
from typing import List, Tuple
from datetime import datetime
#import Birthdays
#import Mailsystem
#import MobilepayBox


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Could you not put me in the Chores2.csv file? I never use the kitchen and probably moving soon. thx.

# Global dictionary to edit chores
# 2, 4, 6 are breaks
# 7 and above are a period where you have no chores. 
# It cycles through the chores in the order of the keys.
# Keep the tail of the rotation chore free to allow flexibility in members.
chore_names = {
    1: "laundry duty",
    3: "trash duty",
    5: "Pant duty",
    7: "Kitchen Captain"
}


class Member:
    def __init__(self, id: int, name: str):
        self.id = int(id)
        self.name = name


# Reads Chores2.csv in the same directory as the script
def read_csv(file_path: str, encoding: str = 'iso-8859-1') -> List[List[str]]:
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            return [row for row in reader if row]
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return []
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return []


# Writes data to Chores2.csv
def write_csv(file_path: str, data: List[List[str]]) -> None:
    try:
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        logging.info(f"CSV file saved: {file_path}")
    except Exception as e:
        logging.error(f"Error writing to CSV file: {e}")


# Rotates members through the chores
def rotate_members(members: List[Member]) -> List[Member]:
    total_members = len(members)
    return [Member((member.id % total_members) + 1, member.name) for member in members]


# Formats the chore update strings
def generate_chore_update_string(members: List[Member], current_week: int) -> str:
    chore_update = f"Chore Update 🙌\n\nWeek: {current_week}\n\n"
    sorted_members = sorted(members, key=lambda member: member.id)
    
    for member in sorted_members:
        if member.id in chore_names:
            chore_update += f"{member.name} on {chore_names[member.id]}\n\n"

    return chore_update.strip()


# Removes a member from the list. Behaves differently if the member is in the inner chore cycle or not. 
def remove_member(members: List[Member], id_to_remove: int) -> List[Member]:
    max_chore_id = max(chore_names.keys())

    members = [member for member in members if member.id != id_to_remove]

    if id_to_remove <= max_chore_id:
        for member in members:
            if member.id <= id_to_remove:
                member.id += 1
        
        max_id_member = max(members, key=lambda member: member.id)
        if max_id_member.id != 1:
            max_id_member.id = 1
    else:
        for member in members:
            if member.id > id_to_remove:
                member.id -= 1

    logging.info("Updated members after removal:")
    for member in members:
        logging.info(f"ID: {member.id}, Name: {member.name}")

    return members


# Adds a new member to the end of the list
def add_member(members: List[Member], new_member_name: str) -> List[Member]:
    new_member_id = max(member.id for member in members) + 1
    new_member = Member(new_member_id, new_member_name)
    members.append(new_member)
    return members


# A little UI to rotate or remove/add members
def handle_choice(members: List[Member], members_data: List[List[str]]) -> Tuple[str, int, List[Member]]:
    while True:
        choice = input("(R)emove, (A)dd, or progress to next (W)eek?: ").lower()
        
        if  choice.lower() == 'r':
            try:
                member_id = int(input("Enter member ID to remove: "))
                members = remove_member(members, member_id)
            except ValueError:
                logging.warning("Invalid ID. Please enter a number.")
            continue
        
        elif choice.lower() == 'a':
            new_member_name = input("Enter new member name: ")
            members = add_member(members, new_member_name)
            continue
        
        elif choice.lower() == 'w':
            current_week = datetime.now().isocalendar()[1]
            rotated_members = rotate_members(members)
            chore_update_string = generate_chore_update_string(rotated_members, current_week)
            return chore_update_string, current_week, rotated_members
        
        else:
            logging.warning("Invalid choice. Please try again.")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    members_file_path = os.path.join(script_dir, 'Chores2.csv')
    members_data = read_csv(members_file_path)
    if not members_data:
        return
    
    members = [Member(row[0], row[1]) for row in members_data[1:]] # Skip the first row with the week number 1:
    current_week = datetime.now().isocalendar()[1]
    
    logging.info(f"Current week: {current_week}")
    logging.info("Current members:")
    for member in members:
        logging.info(f"{member.id}: {member.name}")

    chore_update, _, rotated_members = handle_choice(members, members_data)
    message = f"\n{chore_update}\n\n"
    message += "...........................................\n\n"
    message += "Link to 1C Excel:\n"
    message += "https://1drv.ms/x/s!Al20EjOYLuEYrxJf2dnFPydZZfbA?e=yynfEH&nav=MTVfe0FGMzhFMjMwLTA5OTUtNEZDMi05MkJELUZDOTRDNUE4NTM3Nn0"
    pyperclip.copy(message)
    logging.info("Message copied to clipboard.")
    print(message)

    if input("Do you want to save the changes to the CSV file? (y/n): ").lower() == 'y':
        rotated_members_data = [[member.id, member.name] for member in rotated_members]
        write_csv(members_file_path, [[current_week]] + rotated_members_data)


if __name__ == "__main__":
    main()
