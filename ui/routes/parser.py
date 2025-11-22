from flask import Blueprint, render_template

from scrapers.default.db import ScraperDb

blueprint = Blueprint('parser', __name__)


@blueprint.route('/parser')
def route_parser():
    db = ScraperDb(database='scraper')
    pages = db.get_root_pages()

    return render_template('parser.html', active_page='parser', pages=pages)
