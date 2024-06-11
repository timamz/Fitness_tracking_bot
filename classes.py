import csv
from datetime import datetime, date, timedelta
from typing import List

class Exercise:
    def __init__(self, name: str, setup: str, sets: int, reps: List[str], weight: List[str], rest_time: float) -> None:
        self.name = name
        self.setup = setup if setup != '-' else None
        self.sets = sets
        self.reps = reps
        self.weight = weight
        self.rest_time = rest_time


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
    

    def process_exercise():
        pass
    

    def edit():
        pass 
        # TODO: add regex to check for editing
        

class Workout:
    def __init__(self, path_to_csv: str) -> None:
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
            reader = csv.reader(f)
            for row in reader:
                name = row[0]
                setup = row[1]
                sets = int(row[2])
                reps = [rep for rep in row[3].split('/')]
                weights = [weight for weight in row[4].split('/')]
                rest_time = float(row[5])
                
                exercise = Exercise(name, setup, sets, reps, weights, rest_time)
                self.exercise_list.append(exercise)


    def end(self) -> None:
        end_time = datetime.now()
        self.logs['end_time'] = end_time.strftime("%H:%M:%S")
        hours, minutes, seceonds = self.calculate_passed_time()
        self.logs['duration'] = hours * 60 + minutes


    # used for logging complexity and extra notes after workout
    def log_feedback(self, feedback_type: str, message: str) -> None:
        self.logs[feedback_type] = message


    def calculate_passed_time(self) -> tuple:
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return int(hours), int(minutes), int(seconds)
    
    
    def get_passed_time(self) -> str:
        hours, minutes, seceonds = self.calculate_passed_time()
        return f'{hours} hours, {minutes} minutes, {seceonds} seconds has passed'



if __name__ == '__main__':
    import time
    w = Workout('programs/chest.csv')
    time.sleep(2)
    print(w.get_passed_time())
    time.sleep(2)
    w.end()
    print(w.logs)