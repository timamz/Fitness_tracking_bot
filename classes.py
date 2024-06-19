import csv
from datetime import datetime, date
from typing import List
from itertools import cycle


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
        reps_str = '/'.join(map(str, self.reps)) if self.reps is not None else '-'
        weights_str = '/'.join(map(str, self.weight))
        return (f"Exercise: {self.name}\n"
                f"Setup: {self.setup}\n"
                f"Sets: {self.sets}\n"
                f"Reps: {reps_str}\n"
                f"Weight: {weights_str}\n"
                f"Rest Time: {self.rest_time}\n"
                f"Increment: {self.increment}")
        

class Workout:
    def __init__(self, path_to_csv: str) -> None:
        self.path = path_to_csv
        self.start_time = datetime.now()
        self.logs = {
            "name": (path_to_csv.split('/')[-1]).split('.')[0],
            "date": date.today().strftime("%Y.%m.%d"),
            "start_time": self.start_time.strftime("%H:%M:%S"),
            "end_time": None,
            "duration": None
        }
        self.exercise_list = []

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
                self.exercise_list.append(exercise)

        self.exercise_list_gen = iter(self.exercise_list)
        self.current_exercise = None
        
    
    def __str__(self) -> str:
        res = ''
        for ex in self.exercise_list:
            res += f'{str(ex)}\n\n'
        return res


    def end(self) -> str:
        end_time = datetime.now()
        self.logs['end_time'] = end_time.strftime("%H:%M:%S")
        hours, minutes = self.calculate_passed_time()
        self.logs['duration'] = hours * 60 + minutes
        self.send_logs("logs.csv")

        return (f"{self.logs['name'].capitalize()} workout is done!\n"
                f"Today you have trained for {hours} hours, {minutes} minutes"
                f"\n\nTo start a new workout, type /begin")


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
            return f"There are no more exercises for today, please finish the workout.\nTo end the workout, type /end"
        
    
    def get_name(self) -> str:
        return self.logs['name']


    def get_current_exercise(self):
        if self.current_exercise is None:
            return "No current exercise"
        
        return str(self.current_exercise)
    
    
    def reset_current_exercise(self, exercise_name=None) -> bool:
        """
        Resets the current_exercise attribute.
        If exercise_name is provided, it sets the current_exercise to the exercise with that name.
        Otherwise, it resets to the first exercise in the list.
        """
        with open(self.path, 'r') as f:
            reader = list(csv.reader(f))[1:]
            for row in reader:
                if row[0] == exercise_name.capitalize():
                    try:
                        name = row[0]
                        setup = row[1]
                        sets = int(row[2])
                        reps = [rep for rep in row[3].split('/')] if row[3] != '-' else None
                        weights = [weight for weight in row[4].split('/')]
                        rest_time = float(row[5])
                        increment = float(row[6])
                        sets_limit = int(row[7])
                        
                        self.current_exercise = Exercise(name, setup, sets, reps, weights, rest_time, increment, sets_limit)
                        return 0
                    except BaseException:
                        return 1
    

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
            res = self.reset_current_exercise(exercise_name)
            if res == 0:
                return f"{header[column_index].capitalize()} for {exercise_name} has been updated to {new_value}"
            else:
                return "An error occurred while updating the exercise"
        else:
            return f"Exercise {exercise_name} not found"
    
    
    def send_logs(self, path_to_csv: str) -> None:
        with open(path_to_csv, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.logs['name'], self.logs['date'], self.logs['start_time'], self.logs['end_time'], self.logs['duration']])
            
            
    def calculate_expected_time(self) -> int:
        total = 30 # warmup, waiting for someone, setting up, etc
        for ex in self.exercise_list:
            total += ex.sets + ex.rest_time * ex.sets # one set takes one minute (it is technically ex.sets * 1)
        return total
    

class TrainingProgram:
    def __init__(self, paths: List[str]) -> None:
        self.workouts_paths = cycle(paths)
        self.current_workout_path = next(self.workouts_paths)
        self.workout = None
        
    
    def start_workout(self) -> None:
        self.workout = Workout(self.current_workout_path)
    
    
    def move_to_next_workout(self) -> None:
        self.current_workout_path = next(self.workouts_paths)
