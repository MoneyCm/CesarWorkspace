import webbrowser
import urllib.parse

def get_search_links(component_name):
    query = urllib.parse.quote(component_name)
    return {
        "MercadoLibre CO": f"https://listado.mercadolibre.com.co/{query}",
        "eBay": f"https://www.ebay.com/sch/i.html?_nkw={query}"
    }

def open_search(url):
    webbrowser.open(url)
