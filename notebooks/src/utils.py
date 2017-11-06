from datetime import date, timedelta

def date_range(start=None, end=None):
    y1, m1, d1 = [int(item) for item in start.split('-')]
    start = date(y1, m1, d1)
    y2, m2, d2 = [int(item) for item in end.split('-')]
    end = date(y2, m2, d2)
    span = end - start
    dr = []
    for i in range(span.days + 1):
        dr.append(str(start + timedelta(days=i)))
    return dr

def sql_to_csv(file_path):
    '''Read file of stringified SQL table, transform it to CSV string
    '''
    lines = sql_to_lists(file_path)
    csv_lines = [','.join(line) for line in lines]
    csv_lines[0] = '# ' + csv_lines[0]
    csv_lines = '\n'.join(csv_lines)
    return csv_lines


def sql_to_lists(file_path):
    '''Read file of stringified SQL table, transform it to list of lists
    '''
    with open(file_path) as f:
        raw_lines = f.readlines()
    table = []
    for raw_line in raw_lines:
        row = [column.strip() for column in raw_line.split('|')][1:-1]
        if len(row) == 0:
            continue
        table.append(row)
    return table

#file_path = '../../../data/dates.txt'
# file_path = '../../../aou_enrollment/data/raw/simplified_race_and_gender.txt'
#print(len(sql_to_lists(file_path)))