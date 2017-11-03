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