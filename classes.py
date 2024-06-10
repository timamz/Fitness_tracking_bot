import csv


class Exercise:
    def __init__(self, name: str, setup: str, sets: int, reps: list[int], weight: list[float], rest_time: list[float]) -> None:
        self.name = name
        self.setup = setup if setup != '-' else None
        self.sets = sets
        self.reps = reps
        self.weight = weight
        self.rest_time = rest_time


class Workout:
    def __init__(self, path_to_csv: str) -> None:
        self.exercise_list = None
        self.path_to_csv = path_to_csv

    
    def parse_exercises(self) -> None:
        exercises = []

        with open(self.path_to_csv, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                name = row[0]
                setup = row[1]
                sets = int(row[2])
                reps = [int(rep) for rep in row[3].split('/')]
                weights = [float(weight) for weight in row[4].split('/')]
                rest_times = [float(rest_time) for rest_time in row[5].split('/')]
                
                exercise = Exercise(name, setup, sets, reps, weights, rest_times)
                exercises.append(exercise)
                
        self.exercise_list = exercises
        