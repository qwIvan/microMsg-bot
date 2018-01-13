def test_keyword_by_suffix():
    from .rule import keyword_by_suffix
    assert keyword_by_suffix('呵呵.jpg') == ('呵呵', 1)
    assert keyword_by_suffix('  呵呵  .gIf    ') == ('呵呵', 1)
    assert keyword_by_suffix('  呵呵   .jpG    *3   ') == ('呵呵', 3)
    assert keyword_by_suffix('  呵呵   .Png    *6   ') == ('呵呵', 5)
    assert keyword_by_suffix('     .WebP    ') == ('', 1)
    assert keyword_by_suffix('     故事.WebP    ') == ('故事', 1)


def test_keyword_by_at():
    from .rule import keyword_by_at
    assert keyword_by_at('@流氓   呵呵  ', '流氓') == ('呵呵', 1)
    assert keyword_by_at('@流氓  @流氓 呵呵', '流氓') == ('@流氓 呵呵', 1)
    assert keyword_by_at('@流氓   呵呵  * 2', '流氓') == ('呵呵', 2)
    assert keyword_by_at('@流氓   呵呵  * 88', '流氓') == ('呵呵', 5)


def test_meme_url():
    from . import meme
    return meme.image_url('呵呵')

