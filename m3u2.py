from m3u_parser import M3uParser

url = "https://iptv-org.github.io/iptv/languages/hin.m3u"
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
working_streams = []
non_working_streams = []

for stream in streams:
    if stream['status'] == 'GOOD':
        working_streams.append(stream)
    else:
        non_working_streams.append(stream)

# Display working streams
print("Working streams:")
for stream in working_streams:
    print(stream['name'], stream['url'])

# Display non-working streams
print("\nNon-working streams:")
for stream in non_working_streams:
    print(stream['name'], stream['url'])

# Convert streams to JSON and save to a file
parser.to_file('streams.json')
