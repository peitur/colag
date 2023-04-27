# colag

## packages
python36-requests
python36-setuptools

## Description
Simple python based file batch collector

 - collect.py : generic download of files
 - gemcollect.py : get gem files with deps.
 - list2checksum.py : checksum per line (not collector)
 - pipjig.py : get packages from pypi with references
 - rsmatic.py : rsync large datavolumes (e.g. get repos and such)
 - trailer.py : get rust cargo packages with deps
 - gitat.py : handle batches of git repos


## collect.py

**collect.py** [<conf.json>] <batch.name>

Batch.name is the name of the file in collect.d without the file ending. 

Tool will download  fiels specified in **<batch.json>** in **collect.d** directory.
The tool will get file  (with signature if soecified) and create a reference meta file (appending .json) with info regarding the download.

**NOTE** The checksums are made on the downloaded file itself. 

**NOTE** Signatures are currently not verified autoamtically. This is expected to be done manually by tool user.

Main config file:
```json
[{
    "checksum":"sha256",
    "target":"/storage/collected/files"
}]
```

Main config options are:
- checksum : checksum algorith to use, sha1, sha224, sha256, sha384, sha512.  Default is sha256.
- target : where to put files.


Metafile content:
```json
[
  {
    "01.filename": "test/cve/allitems.csv.gz",
    "02.source": "https://cve.mitre.org/data/downloads/allitems.csv.gz",
    "03.atime": "2021-11-12T10:22:48.835429",
    "04.ctime": "2021-11-12T10:22:52.904935",
    "05.mtime": "2021-11-12T10:22:52.904935",
    "06.size": 146285072,
    "07.checksum": "sha256:8c1e402593e47dbf0be37705e62b91e5e06834221b2fde6b503726e3fc550e09"
  }
]
```


Example config:
```json
[
  {
    "version":"2205.0.0",
    "bsize":"8192",
    "url":"https://stable.release.core-os.net/amd64-usr/current/coreos_production_virtualbox_image.vmdk.bz2",
    "filename":"coreos_production_virtualbox_image-v<% version %>.vmdk.bz2"
  },
  {
    "version":"1.17.3",
    "url":"https://nginx.org/download/nginx-<% version %>.tar.gz",
    "signature":"https://nginx.org/download/nginx-<% version %>.tar.gz.asc"
  }
]
```

Supported options per item:
- version : variable used with URL, replace  <% version %> string.
- bsize : buffer size
- url : the path to the file to get.
- filename : target filename, name of file to store to.
- signature : signature file to also get.


## gemcollect.py

**gemcollect.py** [<conf.json>] <gemfile>



## list2checksum.py



## pipjig.py

**pipjig.py** [<conf.json>] <requirements.txt> 
##  rsmatic.py

**rsmatic.py** <batch-file>

Batch rsync transfers.

batchfile format is in list of json structures:
```json
[
    {
        "debug": true,
        "source":"<rsyncsite>",
        "target":"<targetrootpath>",
        "logfile":"logfilepath_mirror.log",
        "options":{
            "bandwidth":"4096",
            "delete-after":true,
            "times":true, 
            "ignore-errors":true,
            "exclude":[]
        }
    }
]
```
 - source: rsync site to sync
 - target: where to store locally
 - logfile: lgfile for rsync
 - options: rsync options

## trailer.py

**trailer.py** <batchfile>
 
## gitat.py
 Handles batches of git repos
 
Main config
```json
[
	{
		"debug":"no",
		"target":"test"
	}
]
```
 
Example of batch file
```json
[
    {
        "repo":"https://github.com/peitur/colag.git",
        "rename":"collecors"
    },{
        "repo":"https://github.com/peitur/shell-utils"
    }
]
```
