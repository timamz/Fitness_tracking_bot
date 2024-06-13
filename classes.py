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
        reps_str = '/'.join(map(str, self.reps)) if self.reps is not None else '-'
        weights_str = '/'.join(map(str, self.weight))
        return (f"Exercise: {self.name}\n"
                f"Setup: {setup_str}\n"
                f"Sets: {self.sets}\n"
                f"Reps: {reps_str}\n"
                f"Weight: {weights_str}\n"
                f"Rest Time: {self.rest_time}")
        

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
        exercise_list = []

        with open(path_to_csv, 'r') as f:
            reader = list(csv.reader(f))[1:]
            for row in reader:
                name = row[0]
                setup = row[1]
                sets = int(row[2])
                reps = [rep for rep in row[3].split('/')] if row[3] != '-' else None
                weights = [weight for weight in row[4].split('/')]
                rest_time = float(row[5])
                increment = float(row[6])
                sets_limit = int(row[7])
                
                exercise = Exercise(name, setup, sets, reps, weights, rest_time, increment, sets_limit)
                exercise_list.append(exercise)

        self.exercise_list_gen = iter(exercise_list)
        self.current_exercise = next(self.exercise_list_gen)


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
    

    def increment_row_reps(self, row: List[str]) -> None:
        parts = row[3].split('/')
        new_parts = []
        for part in parts:
            if part.isdigit():
                new_parts.append(str(int(part) + 1))
            # if superset, e.g. 7+4/7+4
            else:
                singles = part.split('+')
                singles = [str(int(x) + 1) for x in singles]
                new_parts.append('+'.join(singles))

        row[3] = '/'.join(new_parts)


    def increment_row_weight(self, row: List[str]):
        increment = float(row[-2])
        parts = row[4].split('/')
        new_parts = []
        for part in parts:
            if part.isdigit():
                new_parts.append(str(float(part) + increment))
            # if superset, e.g. 7+4/7+4
            else:
                singles = part.split('+')
                singles = [str(float(x) + increment) for x in singles]
                new_parts.append('+'.join(singles))

        row[4] = '/'.join(new_parts)
        row[3] = '-' # reset reps 

    
    def progress(self):
        with open(self.path, mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

        header = rows[0]
        data_rows = rows[1:]

        for row in data_rows:
            increment_weight = False
            parts = row[3].split('/')
            for part in parts:
                if part.isdigit() and int(part) >= int(row[7]):
                    increment_weight = True
                    break
                # if superset, e.g. 7+4/7+4
                else:
                    singles = part.split('+')
                    for single in singles:
                        if int(single) >= int(row[7]):
                            increment_weight = True
                            break
                        
            self.increment_row_weight(row) if increment_weight else self.increment_row_reps(row)
                        

        with open(self.path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_rows)

    
    def next_exercise(self) -> str:
        try:
            self.current_exercise = next(self.exercise_list_gen)
            return "Moving to the next exercise"
        except StopIteration:
            self.current_exercise = None
            return "There are no more exercises for today, please finish the workout"



    def get_current_exercise(self):
        if self.current_exercise is None:
            return "No current exercise"
        
        return str(self.current_exercise)
    

    def edit_exercise(self, column_name: str, exercise_name: str, new_value: str) -> str:
        column_name = column_name.capitalize()
        exercise_name = exercise_name.capitalize()
        
        with open(self.path, mode='r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

        header = rows[0]
        data_rows = rows[1:]
        column_index = header.index(column_name)
        exercise_found = False

        for row in data_rows:
            if row[0] == exercise_name:
                row[column_index] = new_value
                exercise_found = True
                break

        if exercise_found:
            with open(self.path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(data_rows)
            return f"{exercise_name.capitalize()} {column_index} has been updated to {new_value}"
        else:
            return f"Exercise {exercise_name} not found"
    


if __name__ == '__main__':
    w = Workout('programs/chest.csv')
    for i in range(4):
        print(w.get_current_exercise())
        print(' ')
        print(w.next_exercise())
        print(' ')
