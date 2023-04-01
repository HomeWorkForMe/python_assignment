import os
import sys
import math
from pathlib import Path
from flask import request, jsonify
from werkzeug.exceptions import NotFound
from sqlalchemy.sql import func
import datetime
# Add path to access the model.py
parent_dir = os.path.join(Path.cwd(), os.pardir)
sys.path.append(parent_dir)
print(os.listdir(Path.cwd()))
from model import FinancialData, app


def validate(date_text):
    try:
        datetime.date.fromisoformat(date_text)
        return True
    except ValueError:
        return False


@app.route('/api/financial_data', methods=['GET'])
def get_financial_data():
    response = dict()
    error_message = ''
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not validate(start_date) or not validate(end_date):
        error_message = 'Incorrect data format, should be YYYY-MM-DD'
    symbol = request.args.get('symbol')
    limit = int(request.args.get('limit', 5))
    page = int(request.args.get('page', 1))
    if not all({start_date, end_date, symbol, limit, page}):
        error_message = 'Data incomplete, make sure to provide all arguments'

    data = []
    pagination = []
    response['info'] = {'error': ''}
    if not error_message:
        # Query data from start to end
        query = FinancialData.query
        query = query.filter(FinancialData.symbol == symbol)
        query = query.filter(FinancialData.date >= start_date)
        query = query.filter(FinancialData.date <= end_date)
        query = query.order_by(FinancialData.date)

        # The data
        total_count = query.count()
        num_pages = math.ceil(total_count / limit)
        try:
            objs = query.paginate(page=page, per_page=limit)
            data = [{
                'symbol': item.symbol,
                'date': item.date,
                'open_price': item.open_price,
                'close_price': item.close_price,
                'volume': item.volume
            } for item in objs.items]
            # Pagination
            pagination = {
                'count': total_count,
                'page': page,
                'limit': limit,
                'pages': num_pages
            }

        except NotFound:
            error_message = 'Cannot query data. Please check your page and limit arguments'

    response['data'] = data
    response['pagination'] = pagination
    response['info']['error'] = error_message
    return jsonify(response)


@app.route('/api/statistics', methods=['GET'])
def get_statistics_data():
    response = dict()
    error_message = ''
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not validate(start_date) or not validate(end_date):
        error_message = 'Incorrect data format, should be YYYY-MM-DD'
    symbol = request.args.get('symbol')
    if not all({start_date, end_date, symbol}):
        error_message = 'Data incomplete, make sure to provide all arguments'

    data = []
    response['info'] = {'error': ''}
    if not error_message:
        # Query data from start to end
        query = FinancialData.query
        query = query.filter(FinancialData.symbol == symbol)
        query = query.filter(FinancialData.date >= start_date)
        query = query.filter(FinancialData.date <= end_date)

        average_daily_open_price = query.with_entities(func.avg(FinancialData.open_price).label('average')).all()[0][0]
        average_daily_close_price = query.with_entities(func.avg(FinancialData.close_price).label('average')).all()[0][0]
        average_daily_volume = query.with_entities(func.avg(FinancialData.volume).label('average')).all()[0][0]

        # Rounding
        if average_daily_open_price is not None:
            average_daily_open_price = round(average_daily_open_price, 2)
        if average_daily_close_price is not None:
            average_daily_close_price = round(average_daily_close_price, 2)
        if average_daily_volume is not None:
            average_daily_volume = round(average_daily_volume, 2)
        data = {
            'start_date': start_date,
            'end_date': end_date,
            'symbol': symbol,
            'average_daily_open_price': average_daily_open_price,
            'average_daily_close_price': average_daily_close_price,
            'average_daily_volume': average_daily_volume

        }

    response['data'] = data
    response['info']['error'] = error_message
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
