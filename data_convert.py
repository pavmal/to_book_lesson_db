import json
import data

with open('goals.txt', 'w') as f:
    json.dump(data.goals, f)

with open('teachers.txt', 'w') as f:
    json.dump(data.teachers, f)
