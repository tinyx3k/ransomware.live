<div align="center">
<h1>
  <a href="https://www.ransomware.live">
    ransomware.live 
  </a>
</h1>
</div>

<p align="center">
  <a href="https://github.com/jmousqueton/ransomwatch/actions/workflows/codeql-analysis.yml">
    <img src="https://github.com/jmousqueton/ransomwatch/actions/workflows/codeql-analysis.yml/badge.svg" alt="ransomwatch codeql-analysis analysis" />
  </a>
  <a href="https://github.com/jmousqueton/ransomwatch/actions/workflows/ransomwatch.yml">
    <img src="https://github.com/jmousqueton/ransomwatch/actions/workflows/ransomwatch.yml/badge.svg" alt="ransomwatch engine" />
  </a>
  <a href="https://github.com/jmousqueton/ransomwatch/actions/workflows/ransomwatch-build.yml">
    <img src="https://github.com/jmousqueton/ransomwatch/actions/workflows/ransomwatch-build.yml/badge.svg" alt="ransomwatch dockerimage builder" />
  </a>
  <a href="https://github.com/jmousqueton/ransomwatch/actions/workflows/codeql-analysis.yml">
    <img src="https://github.com/jmousqueton/ransomwatch/actions/workflows/codeql-analysis.yml/badge.svg" alt="ransomwatch codeql analysis" />
  </a>
</p>

[Ransomware.live](https://www.ransomware.live) is a website powered by a modified version of [ransomwatch](https://github.com/joshhighet/ransomwatch).

Ransomware.live is an Ransomware gang tracker, running within github actions, groups are visited & posts are indexed within this repository every hour

missing a group ? try the [_issue template_](https://github.com/jmousqueton/issues/new?assignees=&labels=✨+enhancement&template=newgroup.yml&title=new+group%3A+)

```shell
curl -sL https://raw.githubusercontent.com/jmousqueton/ransomwatch/main/posts.json | jq
curl -sL https://raw.githubusercontent.com/jmousqueton/ransomwatch/main/groups.json | jq
```

---

<h4 align="center">⚠️</h4>

<h4 align="center">
  content within `ransomware.live`, `posts.json`, `groups.json` and the `docs/ & source/` directories is dynamically generated based on website of threat actors. <br><br> whilst sanitisation efforts have been taken, by viewing or accessing Ransomware.live generated material you acknowledge you are doing so at your own risk.
</h4>

---

## Contributions 

## Technicals

The [torproxy](https://github.com/jmousqueton/ransomware.live/torproxy) from [**jmousqueton/ransomware.live/torproxy** registry](https://github.com/jmousqueton/jmousqueton/pkgs/container/ransomwatch%2Ftorproxy) is introduced into the github actions workflow as a [service container](https://docs.github.com/en/actions/guides/about-service-containers) to allow onion routing within [ransomwatch.yml](https://github.com/JMousqueton/ransomware.live/blob/main/.github/workflows/ransomwatch.yml)

Where possible [psf/requests](https://github.com/psf/requests) is used to fetch source html. if a javascript engine is required to render the dom [mozilla/geckodriver](https://github.com/mozilla/geckodriver) and [seleniumhq/selenium](https://github.com/SeleniumHQ/selenium) are invoked.

The frontend is ultimatley markdown, generated with [markdown.py](https://github.com/jmousqueton/ransomware.live/blob/main/markdown.py) and served with [docsifyjs/docsify](https://github.com/docsifyjs/docsify) thanks to [pages.github.com](https://pages.github.com)

Any graphs or visualisations are generated with [plotting.py](https://github.com/jmousqueton/ransomware.live/blob/main/plotting.py) with the help of [matplotlib/matplotlib](https://github.com/matplotlib/matplotlib)

_Post indexing is done with a mix of `grep`, `awk` and `sed` within [parsers.py](https://github.com/jmousqueton/ransomware.live/blob/main/parsers.py) - it's brittle and like any  ̴̭́H̶̤̓T̸̙̅M̶͇̾L̷͑ͅ ̴̙̏p̸̡͆a̷̛̦r̵̬̿s̴̙͛ĩ̴̺n̸̔͜g̸̘̈, has a limited lifetime._

[`groups.json`](https://github.com/jmousqueton/ransomware.live/blob/main/groups.json) contains hosts, nodes, relays and mirrors for a tracked group or actor

[`posts.json`](https://github.com/jmousqueton/ransomware.live/blob/main/posts.json) contains parsed posts, noted by their discovery time and accountable group

## Analysis tools

All rendered source HTML is stored within [ransomwatch/tree/main/source](https://github.com/jmousqueton/ransomware.live/tree/main/source) - change tracking and revision history of these blogs is made possible with git

### [screenshotter.py](https://github.com/jmousqueton/ransomare.live/blob/main/screenshotter.py)

_A script to generate high-resolution screenshots of all online hosts within `groups.json`_

### [srcanalyser.py](https://github.com/jmousqueton/ransomware.live/blob/main/srcanalyser.py)

_A [beautifulsoup](https://code.launchpad.net/~leonardr/beautifulsoup/bs4) script to fetch emails, internal and external links from HTML within `source/`_

## Cli operations

_fetching sites requires a local tor circuit on tcp://9050 - establish one with;_

```shell
docker run -p9050:9050 ghcr.io/jmousqueton/ransomwatch/torproxy:latest
```

### Group management

_manage the groups within [groups.json](groups.json)_

#### Add new location (group or additional mirror)

```shell
./ransomwatch.py add --name acmecorp --location abcdefg.onion
```

## Scraping

```shell
./ransomwatch.py scrape 
```

or to force scraping host with `enabled: False`

```shell
./ransomwatch.py scrape --force 1
```


## Parsing

Iterate files within the `source/` directory and contribute findings to `posts.json`

> for a crude health-check across all parsers, use `assets/parsers.sh`

```shell
./ransomwatch.py parse
```

## Generating page

```shell
./ransomwatch.py markdown 
```

## Misc

### Scan well knowd sites for new Ransomware Gang site 

```shell
./asset/source.zsh 
```

### Generate sitemap.xlm 

```shell
./asset/sitemap.sh
```

### Update Ransomware Descripton from [Malpedia](https://malpedia.caad.fkie.fraunhofer.de/)

```shell
./asset/update_description.sh
```

### Update Ransomware Note from [Zscaler ThreatLabz](https://github.com/threatlabz/ransomware_notes)

```shell
./asset/update_notes.sh
```

### Re-order `groups.json` by group name 

```shell
./asset/orderGroups.sh
```

---

_ransomware.live_ is [licensed](https://github.com/jmousqueton/ransomware.live/blob/main/LICENSE) under [unlicense.org](https://unlicense.org)_
