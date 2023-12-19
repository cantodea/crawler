from flask import Flask, request, render_template, send_file, redirect, url_for,  jsonify,session
from keyword_search import search_amazon_products_by_keyword
from asin_search import get_product_info_by_asin
from bestseller_products_search import scrape_bestseller_products
import pandas as pd
import json
import os
from datetime import datetime


from bestsellers_search import get_categories

app = Flask(__name__)
app.secret_key = '123456'
app.config['UPLOAD_FOLDER'] = r'C:\\Users\\User\\OneDrive\\桌面\\crawler\\temporary file'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_region = request.form.get('region')
        session['region'] = selected_region

        keyword = request.form.get('keyword')
        asin_input = request.form.get('asin')

        if keyword:
            print(f"Keyword Search: {keyword} in {selected_region}")
            products = search_amazon_products_by_keyword(keyword, selected_region)
            save_search_results(products)
            return render_template('keyword_results.html', products=products, region=selected_region)

        elif asin_input:
            print(f"ASIN Input: {asin_input} in {selected_region}")
            asins = asin_input.split()
            products = []
            for asin in asins:
                product_info = get_product_info_by_asin(asin, selected_region)
                if 'error' not in product_info:
                    products.append(product_info)
                else:
                    print(f"Error with ASIN {asin}: {product_info['error']}")
                    return render_template('index.html', error=product_info['error'], region=selected_region)
            save_search_results(products)
            return render_template('asin_results.html', products=products, region=selected_region)

    return render_template('index.html', selected_region=session.get('region', 'it'))

@app.route('/process_selected_asins', methods=['POST'])
def process_selected_asins():
    selected_asins = request.form.getlist('selected_asins')
    print(f"Selected ASINs: {selected_asins}")

    products = []
    errors = []

    for asin in selected_asins:
        product_info = get_product_info_by_asin(asin, session.get('region', 'it'))
        if 'error' not in product_info:
            products.append(product_info)
        else:
            error_message = f"ASIN {asin}: {product_info['error']}"
            print(error_message)
            errors.append(error_message)

    save_search_results(products)

    if not products and errors:
        return render_template('index.html', error='；'.join(errors), region=session.get('region', 'it'))
    elif errors:
        return render_template('asin_results.html', products=products, errors=errors, region=session.get('region', 'it'))
    else:
        return render_template('asin_results.html', products=products, region=session.get('region', 'it'))

@app.route('/download_excel')
def download_excel():
    filename = session.get('products_file')
    if not filename:
        return redirect(url_for('index'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        with open(filepath, 'r') as file:
            products = json.load(file)
    except IOError:
        error_message = "Error: File does not appear to exist."
        print(error_message)
        return error_message

    df = pd.DataFrame(products)
    excel_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "exported_data.xlsx")
    df.to_excel(excel_filepath, index=False)
    return send_file(excel_filepath, as_attachment=True)

def save_search_results(products):
    if products:
        filename = f"products_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, 'w') as file:
            json.dump(products, file)
        session['products_file'] = filename

@app.route('/bestsellers', methods=['GET', 'POST'])
def bestsellers():
    region = request.args.get('region') if request.method == 'GET' else request.form.get('region')
    region = region if region else session.get('region', 'it')
    categories = get_categories(region=region)
    return render_template('bestsellers.html', categories=categories, region=region)

@app.route('/get_subcategories', methods=['GET'])
def get_subcategories():
    region = session.get('region', 'it')
    url = request.args.get('url')

    try:
        if not url:
            raise ValueError("URL parameter is missing")

        print(f"Fetching subcategories for URL: {url} and region: {region}")
        subcategories = get_categories(region=region, specific_url=url)
        print(f"Subcategories fetched: {subcategories}")
        return jsonify(subcategories)
    except Exception as e:
        print(f"Error occurred: {e}")
        # 返回一个错误响应
        return jsonify({"error": str(e)}), 500
    

@app.route('/scrape_bestseller_products', methods=['GET'])
def scrape_products():
    category_url = request.args.get('url')
    if not category_url:
        return jsonify({"error": "URL parameter is missing"}), 400

    try:
        print(f"Scraping products from URL: {category_url}")
        products = scrape_bestseller_products(session.get('region', 'it'), category_url)
        return jsonify(products)
    except Exception as e:
        print(f"Error occurred while scraping: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/show_bestsellers')
def show_bestsellers():
    category_url = request.args.get('url')
    if not category_url:
        return render_template('error.html', message='缺少URL参数')

    try:
        print(f"Scraping products from URL: {category_url}")
        products = scrape_bestseller_products(session.get('region', 'it'), category_url)
        return render_template('show_bestsellers.html', products=products)
    except Exception as e:
        print(f"Error occurred while scraping: {e}")
        return render_template('error.html', message=str(e))



if __name__ == '__main__':
    app.run(debug=True)
