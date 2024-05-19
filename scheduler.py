import json
import random
import argparse
from datetime import datetime


#Scheduling class
#Handles the following requirements:
# - Unlimited number of people
# - Preference to not schedule the same group as the previous scheduling run
# - Support for preferences - prefer to be/not to be scheduled with certain people
#Data expectations:
# - Full name, initials, optional preferences, optional contact information
# - Initials are expected to be unique
# - last scheduled details are stored in the same json file
class Scheduler:
    def __init__(self, json_file):
        random.seed(datetime.now().timestamp())
        self.json_file = json_file
        self.load_data()

#Load json data, see requirements above
    def load_data(self):
        with open(self.json_file, 'r') as file:
            self.data = json.load(file)
        p = self.data['people'].copy()
        #only store records with the initials given
        self.all_people=[one for one in p if "initials" in one]
        #load last scheduled list
        self.last_scheduled_people = self.data.get('last_scheduled_people', [])
        #mark only those available for scheduling
        self.remaining_people = [person for person in self.all_people if not person["initials"] in self.last_scheduled_people and self.to_schedule(person)]
    

    def save_data(self):
        self.data['last_scheduled_people'] = self.last_scheduled_people
        with open(self.json_file, 'w') as file:
            json.dump(self.data, file, indent=4)

#returns true if the person is available for scheduling
    def to_schedule(self,person):
        if not "schedule" in person:
            return True
        return person["schedule"]

#find a person within given list by initials
    def find_person(self,p,lst):
        if not "initials" in p:
            return None
        for l in lst:
            if "initials" in l and l["initials"]==p["initials"]:
                return l
        return None

#find a person within given list with only initials given
    def find_person_initials(self,p,lst):
        for l in lst:
            if "initials" in l and l["initials"]==p:
                return l
        return None

#schedule next group
#returns required number of people or empty list
#if not enough people are available for scheduling
    def schedule(self, num_people):
        if len(self.remaining_people)+len(self.last_scheduled_people) < num_people:
            print("Not enough people remaining.")
            return []

        scheduled_people = []

        while len(scheduled_people) < num_people:
            #check if there are still people available for scheduling
            if len(self.remaining_people) == 0:
                #load from all people disregarding the requirement
                #not to schedule those previously scheduled
                for another_person in self.all_people:
                    if another_person and self.to_schedule(another_person) and not self.find_person(another_person,scheduled_people):
                        self.remaining_people.append(another_person)

                self.last_scheduled_people=[]
                if(len(scheduled_people)+len(self.remaining_people)<num_people):
                    print("Unable to schedule due to not enough people")
                    return []
                       
            #add another random selection from available people
            selected_person = random.choice(self.remaining_people)
            self.remaining_people.remove(selected_person)
            scheduled_people.append(selected_person)

            # Check preferences for the selected person
            if 'preferences' in selected_person:
                for pref in selected_person['preferences']:
                    initials, flag = pref['initials'], pref['flag']
                    if flag:
                        if not self.find_person_initials(initials,scheduled_people):
                            person=self.find_person_initials(initials,self.remaining_people)
                            if person:
                                scheduled_people.append(person)
                                self.remaining_people.remove(person)
                    else:
                        person=self.find_person_initials(initials,scheduled_people)
                        if person:
                            scheduled_people.remove(person)


        if len(scheduled_people)>num_people:
            selected_person = random.choice(scheduled_people)
            self.remaining_people.append(selected_person)
            scheduled_people.remove(selected_person)
        # Update state
        self.last_scheduled_people = [i["initials"] for i in scheduled_people]
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
