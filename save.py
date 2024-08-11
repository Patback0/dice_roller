
def reset(dr, file_path):
    dr.past_rolls.clear()
    dr.dice_points = round(dr.dice_points * 1.01)
    on_save(dr, file_path) # save to file

def on_open(dr, file_path):
    with open(file_path, 'r+') as f:
        lines = f.readlines()
        dr.task_points = int(lines[0].strip())
        dr.dice_points = int(lines[1].strip())
        # if len(lines) > 2:
        #     dr.past_rolls = json.loads(lines[2].strip())

def on_save(dr, file_path, save_past_rolls=False):
    with open(file_path, 'w') as f:
        f.seek(0)
        f.write(str(dr.task_points) + '\n')
        f.write(str(dr.dice_points) + '\n')
        # if save_past_rolls and dr.past_rolls:
        #     f.write(json.dumps(dr.past_rolls) + '\n')