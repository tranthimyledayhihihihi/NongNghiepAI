from app.integrations.winmart_price_client import WinMartPriceClient


def test_winmart_record_normalizes_package_price_to_kg():
    client = WinMartPriceClient()
    item = {
        "itemNo": "10198608",
        "sku": "10198608GOI",
        "description": "NGỌC NƯƠNG Gạo thơm 3Kg_KG",
        "longDescription": "NGỌC NƯƠNG Gạo thơm 3Kg_KG",
        "seoName": "ngoc-nuong-gao-thom-3kg_kg--s10198608",
        "mch1Name": "Thực phẩm",
        "price": {"salePrice": 62700, "originPrice": 62700, "publish": True},
        "warehouse": {"availableQuantity": 7},
        "uom": "GOI",
        "uomName": "Gói",
    }

    record = client._item_to_record(item, requested_crop="lua", requested_region="Ha Noi", query="gạo")

    assert record is not None
    assert record["source_name"] == "WinMart"
    assert record["source_type"] == "winmart_retail_price"
    assert record["price"] == 20900
    assert record["metadata"]["package_kg"] == 3


def test_winmart_record_skips_non_food_false_match():
    client = WinMartPriceClient()
    item = {
        "description": "Gáo nhựa Inochi Notoro",
        "mch1Name": "Phi thực phẩm",
        "price": {"salePrice": 42000, "publish": True},
        "warehouse": {"availableQuantity": 59},
        "uom": "CAI",
        "uomName": "Cái",
    }

    record = client._item_to_record(item, requested_crop="gao", requested_region="Ha Noi", query="gạo")

    assert record is None


def test_winmart_record_converts_grams_to_kg():
    client = WinMartPriceClient()
    item = {
        "itemNo": "10242929",
        "sku": "10242929GOI",
        "description": "Cà chua cherry mix 300g",
        "seoName": "hfg-ca-chua-cherry-mix-300g--s10242929",
        "mch1Name": "Thực phẩm",
        "price": {"salePrice": 25900, "publish": True},
        "warehouse": {"availableQuantity": 5},
        "uom": "GOI",
        "uomName": "Gói",
    }

    record = client._item_to_record(item, requested_crop="ca chua", requested_region="TP.HCM", query="cà chua")

    assert record is not None
    assert record["price"] == 86333.33
    assert record["metadata"]["product_name"] == "Cà chua cherry mix 300g"


def test_winmart_record_handles_multipack_grams():
    client = WinMartPriceClient()
    item = {
        "description": "Vinacafe Cà phê hòa tan Special46x17gT12",
        "mch1Name": "Thực phẩm",
        "price": {"salePrice": 166000, "publish": True},
        "warehouse": {"availableQuantity": 63},
        "uom": "GOI",
        "uomName": "Gói",
    }

    record = client._item_to_record(item, requested_crop="ca phe", requested_region="Ha Noi", query="cà phê")

    assert record is not None
    assert round(record["metadata"]["package_kg"], 3) == 0.782
    assert record["price"] == 212276.21
