from osm import get_wikidata_claims


ENTITY = 'Q431648'

def test_get_wikidata_claims():

    assert get_wikidata_claims(entity=ENTITY).__next__ is not None

    claims = {
        key: value
        for key, value in get_wikidata_claims(entity=ENTITY)
    }

    assert claims['P17']['id'] == 'Q4628'
