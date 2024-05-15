import json
import random
import argparse
from datetime import datetime


class Scheduler:
    def __init__(self, json_file):
        random.seed(datetime.now().timestamp())
        self.json_file = json_file
        self.load_data()

    def load_data(self):
        with open(self.json_file, 'r') as file:
            self.data = json.load(file)
        p = self.data['people'].copy()
        self.last_scheduled_people = self.data.get('last_scheduled_people', [])
        self.remaining_people = [person for person in p if not person in self.last_scheduled_people]
    

    def save_data(self):
        self.data['last_scheduled_people'] = self.last_scheduled_people
        with open(self.json_file, 'w') as file:
            json.dump(self.data, file, indent=4)

    def to_schedule(self,person):
        if not "schedule" in person:
            return True
        return person["schedule"]

    def find_person(self,p,lst):
        if not "initials" in p:
            return False
        for l in lst:
            if "initials" in l and l["initials"]==p["initials"]:
                return True
        return False

    def schedule(self, num_people):
        if len(self.remaining_people) < num_people:
            print("Not enough people remaining.")
            return []

        scheduled_people = []

        while len(scheduled_people) < num_people:
            if len(self.remaining_people) == 0:
                print("Unable to fulfill preferences, not enough people.")
                return []

            available_people = [person for person in self.remaining_people if not person in scheduled_people and self.to_schedule(person)]
            selected_person = random.choice(available_people)

            # Check preferences for the selected person
            if 'preferences' in selected_person:
                for pref in selected_person['preferences']:
                    initials, flag = pref['initials'], pref['flag']
                    if flag:
                        for person in self.remaining_people:
                            if person['initials'] == initials and person not in scheduled_people:
                                scheduled_people.append(person)
                                break
                    else:
                        for person in scheduled_people:
                            if person['initials'] == initials:
                                scheduled_people.remove(person)
                                break

            scheduled_people.append(selected_person)

        if len(scheduled_people)>num_people:
            selected_person = random.choice(scheduled_people)
            scheduled_people.remove(selected_person)
        # Update state
        self.last_scheduled_people = scheduled_people
        self.remaining_people = [person for person in self.remaining_people if person not in scheduled_people]

        self.save_data()
        return scheduled_people


def main(args):
    scheduler = Scheduler(args.input)
    scheduled_people = scheduler.schedule(args.count)
    print("Scheduled People:")
    for person in scheduled_people:
        print(person)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Scheduler')
    parser.add_argument('--input', '-i', required=True, dest='input', type=str, help='Input file name')
    parser.add_argument('--count', '-c', dest='count', type=int, default=2, help='Number of people to schedule, must be above 1')
    args = parser.parse_args()
    if args.count<2:
        print("Number of people to count must be >2")
        exit(1)
    try:
        main(args)
    except Exception as ex:
        print(ex)
