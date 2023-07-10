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
working_streams = [stream for stream in streams if stream['status'] == 'GOOD']
non_working_streams = [stream for stream in streams if stream['status'] == 'BAD']

# Display the number of working and non-working links
print("Number of working links:", len(working_streams))
print("Number of non-working links:", len(non_working_streams))

# Create a new M3U file with only the working channels
new_m3u_file = 'working_channels.m3u'

with open(new_m3u_file, 'w') as f:
    for stream in working_streams:
        f.write(f"#EXTINF:-1,{stream['name']}\n{stream['url']}\n")

print("New M3U file with only working channels created:", new_m3u_file)
