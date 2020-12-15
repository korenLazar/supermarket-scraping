from argparse import ArgumentTypeError

from utils import (
    ShufersalCategories,
    is_valid_store_id,
    xml_file_gen,
    create_bs_object,
)


def store_id_type(store_id: str):
    if not is_valid_store_id(int(store_id)):
        raise ArgumentTypeError(f"Given store_id: {store_id} is not a valid store_id.")
    return store_id


def get_store_id(city: str, load_xml: bool):
    """
    This function prints the store_ids of Shufersal stores in a given city.
    The city must match exactly to its spelling in Shufersal's website (hence it should be in Hebrew alphabet).

    :param load_xml: A boolean representing whether to load an existing xml or load an already saved one
    :param city: A string representing the city of the requested store.
    """
    xml_path = xml_file_gen(ShufersalCategories.Stores.name, -1)
    bs_stores = create_bs_object(xml_path, ShufersalCategories.Stores.value, -1, load_xml)

    for store in bs_stores.find_all("STORE"):
        if store.find("CITY").text == city:
            print((store.find("ADDRESS").text[::-1], store.find("STOREID").text, store.find("SUBCHAINNAME").text[::-1]))
