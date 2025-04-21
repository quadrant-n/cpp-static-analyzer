import string

in_str = '\"Test my string.'
my_str = in_str.split('\"')
print(my_str)

whitespaced = 'Test my string.'
stripped = whitespaced.strip()
print(stripped)

separated = 'Test my\tstring\nagain'
splitted = separated.split()
print(splitted)
