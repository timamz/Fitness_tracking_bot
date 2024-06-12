import csv
from datetime import datetime, date, timedelta
from typing import List


class Exercise:
    def __init__(self, name: str, setup: str, sets: int, reps: List[str], weight: List[str], rest_time: float, increment: int, sets_limit: int) -> None:
        self.name = name
        self.setup = setup if setup != '-' else None
        self.sets = sets
        self.reps = reps
        self.weight = weight
        self.rest_time = rest_time
        self.increment = increment
        self.sets_limit = sets_limit


    def __str__(self) -> str:
        setup_str = self.setup if self.setup else 'No setup'
        reps_str = '/'.join(map(str, self.reps))
        weights_str = '/'.join(map(str, self.weight))
        return (f"Exercise: {self.name}\n"
                f"Setup: {setup_str}\n"
                f"Sets: {self.sets}\n"
                f"Reps: {reps_str}\n"
                f"Weight: {weights_str}\n"
                f"Rest Time: {self.rest_time}")
    

    def edit():
        pass 
        # TODO: add regex to check for editing
        

class Workout:
    def __init__(self, path_to_csv: str) -> None:
        self.path = path_to_csv
        self.start_time = datetime.now()
        self.logs = {
            "name": (path_to_csv[9:]).split('.')[0],
            "date": date.today().strftime("%Y.%m.%d"),
            "start_time": self.start_time.strftime("%H:%M:%S"),
            "end_time": None,
            "duration": None,
            "complexity": 7,
            "notes": ''
        }
        self.exercise_list = []

        with open(path_to_csv, 'r') as f:
            reader = list(csv.reader(f))[1:]
            for row in reader:
                name = row[0]
                setup = row[1]
                sets = int(row[2])
                reps = [rep for rep in row[3].split('/')]
                weights = [weight for weight in row[4].split('/')]
                rest_time = float(row[5])
                increment = float(row[6])
                sets_limit = int(row[7])
                
                exercise = Exercise(name, setup, sets, reps, weights, rest_time, increment, sets_limit)
                self.exercise_list.append(exercise)


    def end(self) -> str:
        end_time = datetime.now()
        self.logs['end_time'] = end_time.strftime("%H:%M:%S")
        hours, minutes = self.calculate_passed_time()
        self.logs['duration'] = hours * 60 + minutes

        return (f"{self.logs['name'].capitalize()} workout is done!\n"
                f"Today you have trained for {hours} hours, {minutes} minutes")


    # used for logging complexity and extra notes after workout
    def log_feedback(self, feedback_type: str, message: str) -> None:
        self.logs[feedback_type] = message


    def calculate_passed_time(self) -> tuple:
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return int(hours), int(minutes)
    
    
    def get_passed_time(self) -> str:
        hours, minutes = self.calculate_passed_time()
        return f'{hours} hours, {minutes} minutes'
    

    def increment_reps(self):
        with open(self.path, mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

        header = rows[0]
        data_rows = rows[1:]

        for row in data_rows:
            parts = row[3].split('/')
            new_parts = []
            for part in parts:
                if part.isdigit():
                    new_parts.append(str(int(part) - 1))
                # if superset, e.g. 7+4/7+4
                else:
                    singles = part.split('+')
                    singles = [str(int(x) - 1) for x in singles]
                    new_parts.append('+'.join(singles))

            row[3] = '/'.join(new_parts)

        with open(self.path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_rows)



if __name__ == '__main__':
    w = Workout('programs/chest.csv')
    w.increment_reps()
