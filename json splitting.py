json_test = '[1, 2, 3, 4][9, 8, 7, 6]'

end_bracket = False

for count, letter in enumerate(json_test):
    if end_bracket:
        if letter == '[':
            json_test = json_test[:count] + '|' + json_test[count:]

    end_bracket = False

    if letter == ']':
        end_bracket = True

json_list = json_test.split('|')
