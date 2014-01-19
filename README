SharyLinkCreator
================

This program makes sharing files as easy as a click.

Inspired by Bjoern Schiessle with [ShareLinkCreator][1] written in shell, this is a Python version, that should enables you to have much more control over uploaded files.

It can be used in many ways, but its main goal is to be integrated in file managers, such as Thunar, Dolphin, Nautilus or Nemo.

Usage
-----

The first basic use is to call it with the server name and the file you want to upload:
`sharyLinkCreator -s https://owncloud.example.org/ file1 file2 dir1`

This will create a subdirectory using the current timestamp, upload file1, file2 and recursively all of dir1 in it, create a public share of the whole directory, and give it back to you.

Here is the full argument list:

	  -s SERVER, --server SERVER
	                        Your sharing server, e.g. https://owncloud.example.org
	  -u USERNAME, --username USERNAME
	                        Username
	  -p PASSWORD, --password PASSWORD
	                        Your password
	  --no-recursion        Disable recurse into subfolders [default: False]
	  -v, --verbose         set verbosity level [default: None]
	  -i PATTERN, --include PATTERN
	                        only include paths matching this regex pattern. Note:
	                        exclude is given preference over include. [default:
	                        None]
	  -e PATTERN, --exclude PATTERN
	                        exclude paths matching this regex pattern. [default:
	                        None]
	  -V, --version         show program's version number and exit

Supported services
------------------

For now, only OwnCloud is supported using its [share API][4]. But the modular design should allow easy integration of other services. Patches are welcomed!


Requirements
------------

- python3
- [python-requests][2]
- zenity
- [lxml][3]
- xsel (optional, for clipboard)

This software is distributed under the MIT licence

  [1]: https://github.com/schiesbn/shareLinkCreator
  [2]: http://python-requests.org
  [3]: http://lxml.de
  [4]: http://doc.owncloud.org/server/6.0/developer_manual/core/ocs-share-api.html