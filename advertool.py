

import advertools as adv

adv.crawl('http://www.cettire.com', 'my_output_file.jl', follow_links=True)

# That's it! To open the file:

import pandas as pd

crawl_df = pd.read_json('my_output_file.jl', lines=True)

# https://github.com/prnvvj/Website-SiteMap-Analysis