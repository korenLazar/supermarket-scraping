from argparse import ArgumentTypeError

from utils import ShufersalCategories, create_bs_object, get_download_url, is_valid_store_id, xml_file_gen


def store_id_type(store_id: str):
    if not is_valid_store_id(int(store_id)):
        raise ArgumentTypeError(f"Given store_id: {store_id} is not a valid store_id.")
    return store_id


def get_store_id(city: str, load_xml: bool, logger):
    """
    This function returns the id of a Shufersal store according to a given city.
    The city must match exactly to its spelling in Shufersal's website.

    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    :param city: A string representing the city of the requested store.
    """
    down_url = "" if load_xml else get_download_url(-1, ShufersalCategories.Stores.value)
    bs = create_bs_object(xml_file_gen(ShufersalCategories.Stores.name, -1), down_url)

    for store in bs.find_all("STORE"):
        if store.find("CITY").text == city:
            logger.info((store.find("ADDRESS").text, store.find("STOREID").text, store.find("SUBCHAINNAME").text))