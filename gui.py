from tkinter import Tk, Label, Entry, Button
from m3u_parser import M3uParser

def process_url():
    url = url_entry.get()

    useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"

    # Instantiate the parser
    parser = M3uParser(timeout=5, useragent=useragent)

    # Parse the M3U file
    parser.parse_m3u(url)

    # Remove streams by mp4 extension
    parser.remove_by_extension('mp4')

    # Get the list of all streams
    streams = parser.get_list()

    # Separate working and non-working streams
    working_streams = [stream for stream in streams if stream['status'] == 'GOOD']
    non_working_streams = [stream for stream in streams if stream['status'] == 'BAD']

    # Display the number of working and non-working links
    result_label.config(text="Number of working links: {}\nNumber of non-working links: {}".format(len(working_streams), len(non_working_streams)))

    # Create a new M3U file with only the working channels
    new_m3u_file = 'working_channels.m3u'

    with open(new_m3u_file, 'w') as f:
        for stream in working_streams:
            f.write("#EXTINF:-1,{}\n{}\n".format(stream['name'], stream['url']))

    result_label.config(text=result_label.cget("text") + "\nNew M3U file with only working channels created: {}".format(new_m3u_file))


# Create the GUI window
window = Tk()
window.title("M3U Parser")
window.geometry("400x200")

# URL label and entry
url_label = Label(window, text="M3U URL:")
url_label.pack()

url_entry = Entry(window, width=50)
url_entry.pack()

# Process button
process_button = Button(window, text="Process", command=process_url)
process_button.pack()

# Result label
result_label = Label(window, text="")
result_label.pack()

# Start the GUI event loop
window.mainloop()
