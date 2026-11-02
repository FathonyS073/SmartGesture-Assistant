from pathlib import Path
import pytest
from config import DATA_FILE
from app.services.content_repository import ContentRepository,ContentError

def test_all_ten_distinct_complete_and_referenced():
    repo=ContentRepository()
    assert sorted(repo.menus)==list(range(1,11))
    assert len({m.title for m in repo.menus.values()})==10
    assert len({m.narration_text for m in repo.menus.values()})==10
    assert all(len(m.sections)>=3 for m in repo.menus.values())
    for key,m in repo.menus.items():
        assert key==m.gesture==m.id
        assert m.narration_id==f'menu_{key:02d}'
        assert m.source_urls and all(url.startswith('https://') for url in m.source_urls)
        assert m.verification_status=='DRAF_BELUM_DISAHKAN'
        assert m.last_verified_at is None
        assert len(m.narration_text)>120
    assert 'SIAM' in repo.get(5).narration_text
    assert 'selma' in repo.get(6).narration_text.lower()
    assert '0341-577911' in repo.get(10).summary

def test_missing_and_invalid_json(tmp_path):
    with pytest.raises(ContentError):ContentRepository(tmp_path/'missing.json')
    p=tmp_path/'menus.json';p.write_text('{broken',encoding='utf-8')
    with pytest.raises(ContentError):ContentRepository(p)
    p.write_text('{"menus": []}')
    with pytest.raises(ContentError):ContentRepository(p)
