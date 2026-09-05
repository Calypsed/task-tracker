from database.connection import make_sqlalchemy_url


def test_make_sqlalchemy_url_adds_psycopg_driver():
    url = make_sqlalchemy_url("postgresql://user:password@localhost/db")

    assert url == ("postgresql+psycopg://user:password@localhost/db")


def test_make_sqlalchemy_url_keeps_existing_driver():
    url = make_sqlalchemy_url("postgresql+psycopg://user:password@localhost/db")

    assert url == ("postgresql+psycopg://user:password@localhost/db")


def test_make_sqlalchemy_url_keeps_other_urls_unchanged():
    url = "sqlite:///test.db"

    result = make_sqlalchemy_url(url)

    assert result == url
