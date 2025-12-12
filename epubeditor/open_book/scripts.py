from scripts import TITLE_to_Title


scripts_list = [
    'TITLE_to_Title',
    
]

def main(temp_path, arg):
    args = arg.split()
    action = args[0]
    if action not in scripts_list:
        print("There's no such script:", action)
        return
    
    match action:
        case 'TITLE_to_Title':
            if len(args) > 1:
                query = args[1]
            else:
                query = '//div[@class="title1"]/p'
            TITLE_to_Title(temp_path, query)