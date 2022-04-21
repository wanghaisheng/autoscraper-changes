# GitHub AutoScraper + Change Alerts



## tidb cloud 
 
account create

cluster create

https://github.com/caronc/apprise



```
import apprise

# Create an Apprise instance
apobj = apprise.Apprise()

# Create an Config instance
config = apprise.AppriseConfig()

# Add a configuration source:
config.add('/path/to/my/config.yml')

# Add another...
config.add('https://myserver:8080/path/to/config')

# Make sure to add our config into our apprise object
apobj.add(config)

# You can mix and match; add an entry directly if you want too
# In this entry we associate the 'admin' tag with our notification
apobj.add('mailto://myuser:mypass@hotmail.com', tag='admin')

# Then notify these services any time you desire. The below would
# notify all of the services that have not been bound to any specific
# tag.
apobj.notify(
    body='what a great notification service!',
    title='my notification title',
)

# Tagging allows you to specifically target only specific notification
# services you've loaded:
apobj.notify(
    body='send a notification to our admin group',
    title='Attention Admins',
    # notify any services tagged with the 'admin' tag
    tag='admin',
)

# If you want to notify absolutely everything (reguardless of whether
# it's been tagged or not), just use the reserved tag of 'all':
apobj.notify(
    body='send a notification to our admin group',
    title='Attention Admins',
    # notify absolutely everything loaded, reguardless on wether
    # it has a tag associated with it or not:
    tag='all',
)```


```
import apprise

# Create an Apprise instance
apobj = apprise.Apprise()

# Add at least one service you want to notify
apobj.add('mailto://myuser:mypass@hotmail.com')

# Then send your attachment.
apobj.notify(
    title='A great photo of our family',
    body='The flash caused Jane to close her eyes! hah! :)',
    attach='/local/path/to/my/DSC_003.jpg',
)

# Send a web based attachment too! In the below example, we connect to a home
# security camera and send a live image to an email. By default remote web
# content is cached but for a security camera, we might want to call notify
# again later in our code so we want our last image retrieved to expire(in
# this case after 3 seconds).
apobj.notify(
    title='Latest security image',
    attach='http://admin:password@hikvision-cam01/ISAPI/Streaming/channels/101/picture?cache=3'
)
```