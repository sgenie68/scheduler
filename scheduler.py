import json
import random

class Scheduler:
    def __init__(self, json_file):
        self.json_file = json_file
        self.load_data()

    def load_data(self):
        with open(self.json_file, 'r') as file:
            self.data = json.load(file)
        self.remaining_people = self.data['people'].copy()
        self.last_scheduled_people = []

    def save_data(self):
        with open(self.json_file, 'w') as file:
            json.dump(self.data, file, indent=4)

    def schedule(self, num_people):
        if len(self.remaining_people) < num_people:
            print("Not enough people remaining.")
            return []

        scheduled_people = []

        while len(scheduled_people) < num_people:
            if len(self.remaining_people) == 0:
                print("Unable to fulfill preferences for remaining people.")
                return []

            available_people = [person for person in self.remaining_people if person not in scheduled_people]
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


# Example usage:
scheduler = Scheduler('people.json')
scheduled_people = scheduler.schedule(3)
print("Scheduled People:")
for person in scheduled_people:
    print(person)

