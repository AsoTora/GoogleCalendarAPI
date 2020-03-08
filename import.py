import csv
from glob import glob
import datetime
from datetime import datetime as dday
import calendarapi


def get_info(worker):
    # read csv files to get fiven worker's data
    for file in glob("*.csv"):
        with open(file, 'r') as csv_file:
            csv_dreader = csv.DictReader(csv_file)
            for person in csv_dreader:
                if (person['\ufeff']) == worker:
                    return person
    raise "WorkerNotFoundError"


def send_info(worker):
    shifts = {
        'Night Shift': ['21:00:00', '09:00:00'],
        'Day Shift': ['09:00:00', '21:00:00'],
        '8-hour': ['09:00:00', '17:00:00']
    }
    data = get_info(worker)

    # skip garbage columnes
    for k in ['\ufeff', 'Position', 'Total: Paid hours']:
        data.pop(k)

    # create a DB with all the necessary entries
    for day in data:
        # skip empty days
        shift = data[day]
        if shift == '':
            continue

        info = {}
        date_time_obj = datetime.datetime.strptime(
            '{}-{}'.format(str(dday.now().year), day), "%Y-%a, %b %d")

        info['shift'] = shift
        info['start_date'] = str(date_time_obj.date())
        info['start_time'] = shifts[shift][0]
        info['end_time'] = shifts[shift][1]

        if shift == 'Day Shift' or shift == '8-hour':
            info['end_date'] = info['start_date']
        else:  # Nigth Shift
            try:
                date_time_obj = date_time_obj.replace(
                    day=date_time_obj.date().day + 1)
            except ValueError as e:
                print(e)
                print("Changing month as well")
                # TODO: add diff years handling
                #  date_time_obj.replace(
                #   year=date_time_obj.date().year + 1, day=1, month=1)
                date_time_obj = date_time_obj.replace(
                    month=date_time_obj.date().month + 1, day=1)
            finally:
                info['end_date'] = str(date_time_obj.date())

        calendarapi.create_event(info)


if __name__ == '__main__':
    # TODO: придумать, как использовать service нормально
    send_info('Andrei Shvedau')
