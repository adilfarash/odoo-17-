import base64
import io
from textwrap import wrap

import matplotlib.pyplot as plt

from odoo import models, api


def get_aggregate_vals(k_vals, vals):
    product_dict = {}
    for name, count in zip(k_vals, vals):
        if name in product_dict:
            # If name already exists in the dictionary, accumulate the count
            product_dict[name] += count
        else:
            # Otherwise, add the name to the dictionary with its count
            product_dict[name] = count

    # Extract unique names and aggregated counts from the dictionary
    unique_names = list(product_dict.keys())
    aggregated_counts = list(product_dict.values())
    return unique_names, aggregated_counts


def generate_bar_chart(xlabel, ylabel, min_y, max_y):
    # Label word wrapping
    r_label = ['\n'.join(wrap(l, 16)) for l in xlabel]
    fig, ax = plt.subplots()
    bar_container = ax.bar(r_label, ylabel, width=0.5)
    ax.set(ylabel='Qty Sold', title='Product Count Chart', ylim=(min_y, max_y))
    ax.bar_label(bar_container, fmt='{:,.0f}')
    ax.tick_params(axis='x', labelrotation=90)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    bar_chart_image = base64.b64encode(buffer.getvalue())
    plt.close()
    return bar_chart_image


def generate_pie_chart(x_label, y_data):
    fig, ax = plt.subplots()
    ax.pie(y_data, labels=x_label, autopct='%1.1f%%')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    bar_chart_image = base64.b64encode(buffer.getvalue())
    plt.close()
    return bar_chart_image


def get_min_max_count(count_list):
    return min(count_list) - 1, max(count_list) + 1


class DemoPdf(models.AbstractModel):
    _name = 'report.pdf_demo.print_demo_report'
    _description = 'pdf_demo_print_demo_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        label_limit_count = len(docs)
        bar_charts = {}
        pie_charts = {}
        for order in docs:
            order_lines = order.order_line
            product_names = order_lines.mapped('name')
            product_count = order_lines.mapped('product_uom_qty')
            product_names, product_count = get_aggregate_vals(
                product_names, product_count)
            minimum_count, maximum_count = get_min_max_count(product_count)
            # Bar Chart generation
            image = generate_bar_chart(product_names, product_count,
                                       minimum_count, maximum_count)
            bar_charts.update({
                order.id: image,
            })

            image = generate_pie_chart(product_names, product_count)
            pie_charts.update({
                order.id: image,
            })

        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
            'bar_chart_image': bar_charts,
            'pie_chart_image': pie_charts,
            'label_count_limit': label_limit_count,
            **(data or {})
        }
