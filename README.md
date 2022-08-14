## streeteasy-grep

Query [streeteasy.com](https://www.streeteasy.com) rentals and get the results in json format. Tool also always you to diff between different invocations of the same query.

### Motivation

`streeteasy` currently limits bots and scrapers from accessing the site programmitically with rate-limiting and captcha features.

Using [selenium](https://selenium-python.readthedocs.io/), we're able to replicate non-bot behavior and therefore allowing us to parse the site.

**Note: Even this method gets rate limited sometimes.**
### Installation

First install the Chromium drivers locally (the directions can be found [here](https://selenium-python.readthedocs.io/)), and have a chromium based browser installed. Any browser can be used, but requires changing the driver setup in `parser.py`.

Simple install on Debian based systems:

```
apt-get install -y chromium-chromedriver
```

It currently relies on [poetry](https://python-poetry.org/) for installation and dependency management. Follow the `poetry` docs for installation.

Once `poetry` is installed run:

```
poetry install
```

and

```
poetry shell
```

Should now be able to run the command `streeteasy-grep --help` in a console.

### Usage

```
usage: streeteasy-grep [-h] [--location LOCATION] [--price-lower-bound PRICE_LOWER_BOUND] [--price-upper-bound PRICE_UPPER_BOUND] [--num-bedrooms NUM_BEDROOMS] [--has-fee]
                       [--check-diff] [--num-pages NUM_PAGES]

Parse streeteasy rental results for a given query with given parameters.

optional arguments:
  -h, --help            show this help message and exit
  --location LOCATION, -l LOCATION
                        Location to search for. (default: ues)
  --price-lower-bound PRICE_LOWER_BOUND, -pl PRICE_LOWER_BOUND
                        Lower bound of rental price (default: 0)
  --price-upper-bound PRICE_UPPER_BOUND, -pu PRICE_UPPER_BOUND
                        Upper bound of rental price (default: 3000)
  --num-bedrooms NUM_BEDROOMS, -nb NUM_BEDROOMS
                        Number of bedrooms (default: 1)
  --has-fee, -hf        Include apartments that have a signing fee. (default: False)
  --check-diff, -cd     Check diff between queries if the same query file has been created before (default: False)
  --num-pages NUM_PAGES, -np NUM_PAGES
                        Number of pages to iterate through. (default: 1)
  ```

### Sample Usage

By default running `streeteasy-grep` will generate the query parameters:

```
ues/price:0-3000|beds:1|no_fee|1
```

Translating to querying for a 1 bedroom apartment on the Upper East Side, between $0-$3000/month, only including listing which are `no fee`, and only looking at the first page of results.

The results will be stored in a file called `results-{hash}.json` where `hash` is the hashed query string.

It'll contain a dictionary with the `links` keys, pointing to a object containing `address` and `price`:

```
{"https://streeteasy.com/building/1600-3-avenue-new_york/5c": {"Address": "174 East 90th Street #5C", "Price": "$2,100"}
```

### Checking diff

The tool is useful in checking for new listings using a previous invocation with **the same query**. Simply specifying:

```
streeteasy-grep --check-diff
```

Will diff the new query contents with an existing json file (in the directory the tool is invoked) and print to `stdout`.

### Motivation

The goal is you can setup a automated cron that runs the queries, then runs `--check-diff` and get immediate notifications if a new apartment is listed.
