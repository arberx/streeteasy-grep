#!/usr/bin/env python3

import sys
import json
import pprint
import hashlib
import argparse
import time
import os

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

from streeteasy_grep import config as cfg


def construct_url(args=None):
    """ Construct street easy url given args """

    lower_bound = args.price_lower_bound
    upper_bound = args.price_upper_bound
    location = args.location
    beds = args.num_bedrooms

    url = f"{cfg.STREETEASY_SITE}/for-rent/{location}/price:{lower_bound}-{upper_bound}|beds:{beds}"

    if not args.has_fee:
        url += f"|no_fee"

    return url


def sanitize_link(link):
    """ Santiize link from any non-standard features. """
    if not link:
        return ""

    # Remove query paramaters
    link = link.split("?")[0]
    return link


def check_and_print_difference(object, file):
    """ Print diff if file already exists. """
    if not os.path.exists(file):
        return

    with open(file, "r") as f:
        prev_obj = json.loads(f.read())

    # Print the diff between the two
    pprint.pprint({k: prev_obj[k] for k in set(prev_obj) - set(object)})


def write_to_json(object, file, check_diff=False):
    """ Write json object to a file, if check_diff is True, will return diff of previous file if it exists. """
    if check_diff:
        check_and_print_difference(object, file)

    with open(file, "w+") as f:
        json.dump(object, f)


def parse_args(args):
    """ Parse and store args """
    parser = argparse.ArgumentParser(
        description="Parse streeteasy rental results for a given query with given parameters.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--location", "-l", default="ues", type=str, help="Location to search for."
    )
    parser.add_argument(
        "--price-lower-bound",
        "-pl",
        default=0,
        type=int,
        help="Lower bound of rental price",
    )
    parser.add_argument(
        "--price-upper-bound",
        "-pu",
        default=3000,
        type=int,
        help="Upper bound of rental price",
    )
    parser.add_argument("--num-bedrooms", "-nb", default=1, help="Number of bedrooms")
    parser.add_argument(
        "--has-fee",
        "-hf",
        action="store_true",
        help="Include apartments that have a signing fee.",
    )
    parser.add_argument(
        "--check-diff",
        "-cd",
        action="store_true",
        help="Check diff between queries if the same query file has been created before",
    )
    parser.add_argument(
        "--num-pages",
        "-np",
        default=1,
        type=int,
        help="Number of pages to iterate through.",
    )

    return parser.parse_args(args)


def main(args=None):
    """ Setup and parse results"""
    opts = webdriver.ChromeOptions()
    # opts.headless = True
    with webdriver.Chrome(options=opts) as driver:
        args = parse_args(args)
        url = construct_url(args)

        try:
            # Iterate through all pages of results, an exception will be thrown to end iteration.
            page = 1
            results_dictionary = {}
            while page == args.num_pages:
                print(f"Parsing url: [{url}?page={page}]")
                delay = 3
                time.sleep(1.0)
                driver.get(f"{url}/?page={page}")
                # Wait until the search results are fully loaded
                search_results = WebDriverWait(driver, delay).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "searchCardList"))
                )

                # Start parsing out the result content
                # This is extremely fragile and required looking through the HTML for the class/div ids
                result_list = search_results.find_elements_by_tag_name("li")
                for result in result_list:
                    # Get the listing link
                    a_el = result.find_elements_by_class_name("listingCard-globalLink")
                    link = sanitize_link(a_el[0].get_attribute("href"))
                    # Get the unit address
                    address_el = result.find_elements_by_class_name(
                        "listingCard-addressLabel"
                    )
                    address = address_el[0].text
                    # Get price
                    price_el = result.find_elements_by_class_name("price")
                    price = price_el[0].text

                    results_dictionary[link] = {"Address": address, "Price": price}
                page += 1

        except (WebDriverException, TimeoutException) as e:
            print(f"Error, reached end of results due to: {str(e)}")

        # Write to file using url hash as identifier
        # Also store the query in the output dictionary
        query_content = url.split("for-rent/")[1] + f"|{str(args.num_pages)}"
        hashed_query = hashlib.sha1(query_content.encode()).hexdigest()
        results_dictionary["query"] = query_content

        write_to_json(
            results_dictionary, f"results-{hashed_query}.json", args.check_diff
        )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
