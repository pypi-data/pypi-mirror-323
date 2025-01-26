# ruff: noqa
# belongs in parsers.py
from mijnbib.parsers import Parser


class OpeningHoursParser(Parser):
    def __init__(self, html: str):
        self._html = html

    def parse(self) -> dict(str, tuple):
        """Return list of opening hours.

        >>> html_string = '''
        ... ...
        ... <div class="my-library-user-library-account-list js-accordion">
        ...     <div class="my-library-user-library-account-list__library">
        ...        <h2 class="my-library-user-library-account-list__title ui-accordion-header">
        ...            <div class="my-library-user-library-account-list__title-content">
        ...                Dijk92
        ...                 <span class="region-info">...</span>
        ...            </div>
        ...        </h2>
        ...        <div class="my-library-user-library-account-list__account">
        ...            <div class="my-library-user-library-account-list__basic-info">
        ...                <a href="/mijn-bibliotheek/lidmaatschappen/374047">
        ...                    <div class="my-library-user-library-account-list__name" data-hj-suppress="">Johny</div>
        ...                    <div class="my-library-user-library-account-list__city" data-hj-suppress=""></div>
        ...                </a>
        ...            </div>
        ...            <ul class="my-library-user-library-account-list__info">
        ...                ...
        ...                <li class="my-library-user-library-account-list__loans-link">
        ...                    <a href="/mijn-bibliotheek/lidmaatschappen/374047/uitleningen">Geen uitleningen</a></li>
        ...                <li class="my-library-user-library-account-list__holds-link">
        ...                    <a href="/mijn-bibliotheek/lidmaatschappen/384767/reservaties">5 reserveringen</a></li>
        ...                ...
        ...            </ul>
        ...            ...
        ...        </div>
        ...     </div>
        ... </div>
        ... ...
        ... '''
        >>> AccountsListPageParser(html_string,"https://example.com").parse() # doctest: +NORMALIZE_WHITESPACE
        [Account(library_name='Dijk92', user='Johny', id='374047', loans_count=0, loans_url='https://example.com/mijn-bibliotheek/lidmaatschappen/374047/uitleningen',
                 reservations_count=5, reservations_url='https://example.com/mijn-bibliotheek/lidmaatschappen/384767/reservaties',
                 open_amounts=0, open_amounts_url='')]
        """
