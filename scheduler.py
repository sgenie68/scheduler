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
        self.last_scheduled_people = self.data.get('last_scheduled_people', [])

    def save_data(self):
        self.data['last_scheduled_people'] = self.last_scheduled_people
        with open(self.json_file, 'w') as file:
            json.dump(self.data, file, indent=4)

    def schedule(self, num_people):
        if len(self.remaining_people) < num_people:
            print("Not enough people remaining.")
            return []

        if len(self.remaining_people) == len(self.last_scheduled_people):
            print("All people have been scheduled. Resetting.")
            self.remaining_people = self.data['people'].copy()
            self.last_scheduled_people = []

        print(len(self.last_scheduled_people))
        # Ensure previously scheduled people are not selected
        available_people = [person for person in self.remaining_people if person not in self.last_scheduled_people]
        print(available_people)
        scheduled_people = random.sample(available_people, num_people)

        # Check preferences
        for person in scheduled_people:
            if 'preferences' in person:
                for pref in person['preferences']:
                    initials, flag = pref['initials'], pref['flag']
                    for other_person in scheduled_people:
                        if other_person['initials'] == initials:
                            if (flag and other_person['initials'] not in [p['initials'] for p in person['preferences']]) or (not flag and other_person['initials'] in [p['initials'] for p in person['preferences']]):
                                print(f"Preference violated: {person['name']} ({person['initials']}) and {other_person['name']} ({other_person['initials']})")
                                # Reschedule
                                return self.schedule(num_people)

        # Update state
        self.last_scheduled_people=scheduled_people # Extend instead of assigning directly
        self.remaining_people = [person for person in self.remaining_people if person not in scheduled_people]
        self.save_data()
        return scheduled_people


# Example usage:
scheduler = Scheduler('people.json')
scheduled_people = scheduler.schedule(3)
print("Scheduled People:")
for person in scheduled_people:
    print(person)

