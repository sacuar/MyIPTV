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

# Separate good and bad streams
good_streams = [stream['url'] for stream in streams if stream['status'] == 'GOOD']
bad_streams = [stream['url'] for stream in streams if stream['status'] == 'BAD']

# Display good streams
print("Good streams:")
for url in good_streams:
    print(url)

# Display bad streams
print("\nBad streams:")
for url in bad_streams:
    print(url)

# Convert streams to JSON and save to a file
parser.to_file('streams.json')
