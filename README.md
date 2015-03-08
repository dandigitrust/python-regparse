Python Registry Parser 
=======================
The idea of this started out as one to duplicate Microsoft's autoruns tool to the extent possible with only offline registry hives. Then I started adding extra non-autorun(ish) registry keys and then it turned into more of a Windows Registry parser; hence the name change from autoreg-parse to python-regparse. I'm terrible at naming scripts/tools so this will have to suffice.

I wrote about it here on my blog: https://sysforensics.org/2015/03/python-registry-parser.html

Purpose/Reason
===============
- I didn't like the output of other tools.
- I wanted to learn to write better Python code.

Output
=======
This was a sticky point I had with alternative tools, and realizing this I thought hard and came to the conclusion if I want a tool that doesn't have messy output i'm going to have to make it custom user defined output, and then provide a fallback template file if a custom output isn't defined via the command line. This will likely turn some people off from using this tool, but I think it's the best way forward.

I suggest taking a look here for some output examples: https://sysforensics.org/2015/03/python-registry-parser.html as it's not as complex as it may sound. Even for non-coders it's easy.

How to Install
===============
- Install Python 2.7
- sudo pip install python-registry
- sudo pip install jinja2
- wget https://github.com/sysforensics/python-regparse/blob/master/yapsy_mods/yapsy-master.zip
- Unzip it
- cd yapsy-master/package/
- sudo python setup.py build
- sudo python setup.py install
- wget https://github.com/sysforensics/python-regparse/archive/master.zip
- Unzip
- Put it where you want, and then enjoy!

I've tested/used on OSX and SIFT 3.0 - Should work fine if you follow the directions. Windows should also work fine.

Want to Help?
==============
If you are interested in helping please reach out. Also, feel free to contibute some plugins. If you can't code, but have some ideas please let me know as well. That's almost more important. Just create an issue here on GitHub or if you don't have a GitHub account you can shoot me an email.

Thanks to:
==============
@williballenthin - http://www.williballenthin.com for writing python-registry, which is what I am using under the hood and for the idea of using user defined output.

@hiddenillusion - This example got me started on the idea. https://github.com/williballenthin/python-registry/blob/master/samples/forensicating.py
