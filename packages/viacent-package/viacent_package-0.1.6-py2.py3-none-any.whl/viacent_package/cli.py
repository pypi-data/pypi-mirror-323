import argparse
from viacent_package.count_unique_chars import counter_unique_chars


def process_string(input_string):                                                       #text function
    print(f"Processing string: {input_string}")                                         #print string process
    unique_count = counter_unique_chars(input_string)                                   #call counter function
    print(f"Number of unique characters in string: "
          f"{unique_count}")                                                            #print count result

def process_file(file_path):                                                            #file function
    try:
        with open(file_path, 'r') as file:                                              #open file in read mode
            content = file.read()                                                       #read file content
            print(f"Processing file: {file_path}")                                      #print file process
            unique_count = counter_unique_chars(content)                                #call count function
            print(f"Number of unique characters in file: "
                  f"{unique_count}")                                                    #print result
    except FileNotFoundError:                                                           #file is not found
        print(f"Error: File not found at {file_path}")                                  #print file is not found

def main():                                                                             #function parse arguments
    parser = argparse.ArgumentParser(description="Process a string or a text file.")    #create an argument parser
    parser.add_argument("--string", type=str,
                        help="String to be processed.")                                 #parse argument string
    parser.add_argument("--file", type=str,
                        help="Path to the text file to be processed.")                  #parse argument file
    args = parser.parse_args()                                                          #parse the arguments from cli
    if args.file:                                                                       #argument check
        process_file(args.file)                                                         #call the process_file
    elif args.string:
        process_string(args.string)                                                     #call the process_string
    else:
        print("Error: You must provide either --string or --file parameter.")           #error

if __name__ == "__main__":
    main()
