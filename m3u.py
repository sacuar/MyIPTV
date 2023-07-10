from m3u_parser import M3uParser

url = "https://iptv-org.github.io/iptv/languages/hin.m3u"
useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"

# Instantiate the parser
parser = M3uParser(timeout=5, useragent=useragent)

# Parse the m3u file
parser.parse_m3u(url)

# Remove by mp4 extension
parser.remove_by_extension('mp4')

# Filter streams by status
parser.filter_by('status', 'GOOD')

# Get the list of streams
print(len(parser.get_list()))

# Convert streams to JSON and save to a file
parser.to_file('streams.json')