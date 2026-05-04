from langchain_core.tools import tool
from langchain.docstore.document import Document
from data.mongodb import travel
from model.travel import Ship


@tool
def vacation_lookup(input: str) -> str:
    """find information on vacations and trips"""

    # CHALLENGE: Try adjusting this threshold (0.0 - 1.0).
    # Higher values (e.g. 0.90) return only very close matches — the agent may
    # find fewer or no results for vague queries.
    # Lower values (e.g. 0.50) cast a wider net — results may be less relevant.
    SIMILARITY_THRESHOLD = 0.75

    results = travel.similarity_search_with_score(input, k=4)
    ships = [doc for doc, score in results if score >= SIMILARITY_THRESHOLD]

    content = ""
    for ship in ships:
        content += f" Cruise ship {ship.name} description: {ship.description} with amenities {'/n-'.join(ship.amenities)} "

    return content

@tool
def itinerary_lookup(ship_name:str) -> str:
    """find ship itinerary, cruise packages and destinations by ship name"""
    it = travel.itnerary_search(ship_name)
    results = ""

    for i in it:
        results += f" Cruise Package {i.Name} room prices: {'/n-'.join(i.Rooms)} schedule: {'/n-'.join(i.Schedule)}"

    return results


@tool
def book_cruise(package_name:str, passenger_name:str, room: str )-> str:
    """book cruise using package name and passenger name and room """
    print(f"Package: {package_name} passenger: {passenger_name} room: {room}")

    # LLM defaults empty name to John Doe 
    if passenger_name == "John Doe":
        return "In order to book a cruise I will need to know your name."
    else:
        if room == '':
            return "which room would you like to book"            
        return "Cruise has been booked, ref number is 343242"