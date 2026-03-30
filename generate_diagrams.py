"""Generate diagrams for T1: Code Comprehension"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import networkx as nx
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
# 1. CLASS DIAGRAM
# ─────────────────────────────────────────────
def draw_class_diagram():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_title('Class Diagram – Inventory Management System', fontsize=16, fontweight='bold', pad=20)

    def draw_class_box(ax, x, y, w, h, name, attributes, methods, color='#dce8f5'):
        # Border
        rect = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                               linewidth=1.5, edgecolor='#2c3e50', facecolor=color)
        ax.add_patch(rect)
        # Header
        hdr = FancyBboxPatch((x, y + h - 0.55), w, 0.55, boxstyle='round,pad=0.02',
                              linewidth=0, edgecolor='none', facecolor='#2c3e50')
        ax.add_patch(hdr)
        ax.text(x + w / 2, y + h - 0.27, name, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white')
        # Divider
        ax.plot([x, x + w], [y + h - 0.55, y + h - 0.55], color='#2c3e50', lw=1)
        # Attributes
        row = y + h - 0.85
        for attr in attributes:
            ax.text(x + 0.1, row, attr, fontsize=7, va='center', color='#1a1a2e')
            row -= 0.27
        # Divider 2
        ax.plot([x, x + w], [row + 0.05, row + 0.05], color='#aaa', lw=0.8, linestyle='--')
        row -= 0.05
        # Methods
        for meth in methods:
            ax.text(x + 0.1, row, meth, fontsize=7, va='center', color='#003366')
            row -= 0.27

    def arrow(ax, x1, y1, x2, y2, style='arc3,rad=0', color='#34495e', label='', lw=1.2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                   connectionstyle=style))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 0.12, label, fontsize=7, color=color, ha='center',
                    style='italic')

    # ── IMS (dashboard)
    draw_class_box(ax, 5.8, 6.8, 4.4, 3.0, 'IMS',
        ['- root: Tk', '- lbl_employee: Label', '- lbl_supplier: Label',
         '- lbl_category: Label', '- lbl_product: Label', '- lbl_sales: Label'],
        ['+ __init__(root)', '+ employee()', '+ supplier()', '+ category()',
         '+ product()', '+ sales()', '+ update_content()'],
        color='#cce5ff')

    # ── employeeClass
    draw_class_box(ax, 0.2, 4.5, 3.2, 3.6, 'employeeClass',
        ['- var_emp_id: StringVar', '- var_name: StringVar', '- var_email: StringVar',
         '- var_gender: StringVar', '- var_salary: StringVar'],
        ['+ __init__(root)', '+ add()', '+ show()', '+ get_data(ev)',
         '+ update()', '+ delete()', '+ clear()', '+ search()'])

    # ── supplierClass
    draw_class_box(ax, 0.2, 0.3, 3.2, 3.6, 'supplierClass',
        ['- var_sup_invoice: StringVar', '- var_name: StringVar',
         '- var_contact: StringVar', '- txt_desc: Text'],
        ['+ __init__(root)', '+ add()', '+ show()', '+ get_data(ev)',
         '+ update()', '+ delete()', '+ clear()', '+ search()'])

    # ── categoryClass
    draw_class_box(ax, 3.8, 4.5, 3.2, 2.8, 'categoryClass',
        ['- var_cat_id: StringVar', '- var_name: StringVar'],
        ['+ __init__(root)', '+ add()', '+ show()',
         '+ get_data(ev)', '+ delete()', '+ clear()'])

    # ── productClass
    draw_class_box(ax, 3.8, 0.3, 3.2, 3.6, 'productClass',
        ['- var_cat: StringVar', '- var_sup: StringVar', '- var_pid: StringVar',
         '- var_name: StringVar', '- var_price: StringVar', '- var_qty: StringVar'],
        ['+ __init__(root)', '+ fetch_cat_sup()', '+ add()', '+ show()',
         '+ get_data(ev)', '+ update()', '+ delete()', '+ clear()', '+ search()'])

    # ── salesClass
    draw_class_box(ax, 7.8, 4.5, 3.2, 2.8, 'salesClass',
        ['- blll_list: list', '- var_invoice: StringVar'],
        ['+ __init__(root)', '+ show()', '+ get_data(ev)',
         '+ search()', '+ clear()'])

    # ── billClass
    draw_class_box(ax, 11.5, 0.3, 3.3, 6.8, 'billClass',
        ['- cart_list: list', '- var_cname: StringVar', '- var_contact: StringVar',
         '- var_pid: StringVar', '- var_price: StringVar', '- var_qty: StringVar',
         '- bill_amnt: float', '- net_pay: float', '- discount: float'],
        ['+ __init__(root)', '+ show()', '+ search()', '+ get_data(ev)',
         '+ get_data_cart(ev)', '+ add_update_cart()', '+ bill_update()',
         '+ show_cart()', '+ generate_bill()', '+ bill_top()', '+ bill_middle()',
         '+ bill_bottom()', '+ clear_cart()', '+ clear_all()',
         '+ print_bill()', '+ update_date_time()',
         '+ get_input(num)', '+ clear_cal()', '+ perform_cal()'],
        color='#fff3cd')

    # ── SQLite DB box
    draw_class_box(ax, 7.8, 0.3, 3.2, 3.8, '«database»\nims.db',
        ['employee(eid, name, email, …)', 'supplier(invoice, name, contact, …)',
         'category(cid, name)', 'product(pid, Category, Supplier, …)'],
        [], color='#d4edda')

    # Arrows: IMS creates the module classes
    for (x2, y2), label in [
        ((1.8, 8.1), 'creates'), ((5.4, 7.1), 'creates'),
        ((7.4, 7.1), 'creates'), ((9.2, 7.1), 'creates')
    ]:
        arrow(ax, 8.0, 7.8, x2, y2, color='#2980b9', label=label)

    # IMS -> salesClass
    arrow(ax, 10.2, 7.8, 9.4, 7.1, color='#2980b9', label='creates')

    # productClass -> category/supplier (DB read)
    arrow(ax, 5.4, 2.0, 9.0, 1.8, style='arc3,rad=-0.2', color='#27ae60', label='reads')
    arrow(ax, 5.4, 2.5, 9.0, 2.2, style='arc3,rad=-0.15', color='#27ae60')

    # billClass -> DB
    arrow(ax, 11.5, 2.0, 11.0, 2.0, color='#e74c3c', label='reads/writes')

    # Legend
    ax.text(0.2, 9.7, 'Legend:', fontsize=8, fontweight='bold')
    ax.annotate('', xy=(1.0, 9.5), xytext=(0.4, 9.5),
                arrowprops=dict(arrowstyle='->', color='#2980b9', lw=1.2))
    ax.text(1.1, 9.5, 'creates (instantiates)', fontsize=7, va='center', color='#2980b9')
    ax.annotate('', xy=(3.2, 9.5), xytext=(2.6, 9.5),
                arrowprops=dict(arrowstyle='->', color='#27ae60', lw=1.2))
    ax.text(3.3, 9.5, 'DB read dependency', fontsize=7, va='center', color='#27ae60')
    ax.annotate('', xy=(5.4, 9.5), xytext=(4.8, 9.5),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.2))
    ax.text(5.5, 9.5, 'DB read/write', fontsize=7, va='center', color='#e74c3c')

    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'diagram_class.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#f8f9fa')
    plt.close()
    print(f'Saved: {path}')


# ─────────────────────────────────────────────
# 2. SEQUENCE DIAGRAM – Generate Bill workflow
# ─────────────────────────────────────────────
def draw_sequence_diagram():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    ax.set_title('Sequence Diagram – Generate Bill Workflow', fontsize=15, fontweight='bold', pad=15)

    # Lifeline positions
    lanes = {
        'User': 1.2,
        'billClass\n(UI)': 3.8,
        'productClass\n(UI)': 6.4,
        'SQLite\n(ims.db)': 9.0,
        'Filesystem\n(bill/)': 11.6,
    }
    lane_colors = {
        'User': '#3498db',
        'billClass\n(UI)': '#e67e22',
        'productClass\n(UI)': '#9b59b6',
        'SQLite\n(ims.db)': '#27ae60',
        'Filesystem\n(bill/)': '#c0392b',
    }

    top_y = 9.0
    # Draw actor boxes and lifelines
    for name, x in lanes.items():
        color = lane_colors[name]
        rect = FancyBboxPatch((x - 0.65, top_y), 1.3, 0.55,
                               boxstyle='round,pad=0.05',
                               linewidth=1.5, edgecolor=color, facecolor=color)
        ax.add_patch(rect)
        ax.text(x, top_y + 0.27, name, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white')
        ax.plot([x, x], [top_y, 0.2], color=color, lw=1, linestyle='--', alpha=0.5)

    def msg(ax, x1, x2, y, label, ret=False, color='#2c3e50', note=None):
        style = '<-' if ret else '->'
        lw = 1.2
        ls = '--' if ret else '-'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                   linestyle=ls))
        mx = (x1 + x2) / 2
        ax.text(mx, y + 0.1, label, ha='center', va='bottom', fontsize=7.5,
                color=color, style='italic' if ret else 'normal')
        if note:
            ax.text(max(x1, x2) + 0.15, y, note, ha='left', va='center',
                    fontsize=7, color='gray',
                    bbox=dict(boxstyle='round,pad=0.2', fc='#fffde7', ec='#f0c040', lw=0.7))

    def activation(ax, x, y_top, height, color='#f0c040'):
        rect = FancyBboxPatch((x - 0.12, y_top - height), 0.24, height,
                               boxstyle='square,pad=0',
                               linewidth=1, edgecolor='#888', facecolor=color, alpha=0.7)
        ax.add_patch(rect)

    u, b, p, db, fs = [lanes[k] for k in lanes]

    # Step sequence: (y, x1, x2, label, is_return)
    steps = [
        (8.5, u, b, 'select product from list', False),
        (8.0, b, p, 'show()  [fetch Active products]', False),
        (7.6, p, db, 'SELECT pid,name,price,qty,status FROM product', False),
        (7.2, db, p, 'rows [ ]', True),
        (6.8, p, b, 'populate product_Table', True),
        (6.3, u, b, 'click product row  get_data()', False),
        (5.9, u, b, 'enter Quantity, click "Add|Update Cart"', False),
        (5.5, b, b, 'add_update_cart()  cart_list.append()', False),
        (5.1, b, b, 'bill_update()  calc total, discount, net_pay', False),
        (4.6, u, b, 'enter Customer Name & Contact', False),
        (4.1, u, b, 'click "Generate Bill"', False),
        (3.7, b, b, 'bill_top()  write header to bill area', False),
        (3.3, b, db, 'UPDATE product SET qty=?, status=? WHERE pid=?', False),
        (2.9, db, b, 'OK', True),
        (2.5, b, b, 'bill_bottom()  append totals', False),
        (2.0, b, fs, "open('bill/{invoice}.txt','w').write(bill_text)", False),
        (1.6, fs, b, 'file saved', True),
        (1.2, b, u, 'showinfo("Bill has been generated")', True),
    ]

    for (y, x1, x2, label, is_ret) in steps:
        msg(ax, x1, x2, y, label, ret=is_ret)

    # Activation bars
    activation(ax, b, 8.5, 7.5, color='#fad7a0')
    activation(ax, db, 7.6, 0.8, color='#a9dfbf')
    activation(ax, fs, 2.0, 0.5, color='#f1948a')

    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'diagram_sequence.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Saved: {path}')


# ─────────────────────────────────────────────
# 3. DEPENDENCY GRAPH
# ─────────────────────────────────────────────
def draw_dependency_graph():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_facecolor('#f0f4f8')
    fig.patch.set_facecolor('#f0f4f8')
    ax.set_title('Module Dependency Graph – Inventory Management System',
                 fontsize=15, fontweight='bold', pad=15)

    G = nx.DiGraph()

    project_modules = ['dashboard', 'billing', 'category', 'employee',
                       'product', 'supplier', 'sales']
    stdlib = ['tkinter', 'sqlite3', 'os', 'time', 'tempfile']
    third_party = ['PIL\n(Pillow)']
    external = ['ims.db\n(SQLite)', 'bill/\n(filesystem)']

    for m in project_modules: G.add_node(m, kind='project')
    for m in stdlib:           G.add_node(m, kind='stdlib')
    for m in third_party:      G.add_node(m, kind='third')
    for m in external:         G.add_node(m, kind='external')

    edges = [
        # dashboard imports
        ('dashboard', 'employee'), ('dashboard', 'supplier'),
        ('dashboard', 'category'), ('dashboard', 'product'), ('dashboard', 'sales'),
        ('dashboard', 'tkinter'), ('dashboard', 'PIL\n(Pillow)'),
        ('dashboard', 'sqlite3'), ('dashboard', 'time'), ('dashboard', 'os'),
        # billing imports
        ('billing', 'tkinter'), ('billing', 'PIL\n(Pillow)'), ('billing', 'sqlite3'),
        ('billing', 'time'), ('billing', 'os'), ('billing', 'tempfile'),
        # category imports
        ('category', 'tkinter'), ('category', 'PIL\n(Pillow)'), ('category', 'sqlite3'),
        # employee imports
        ('employee', 'tkinter'), ('employee', 'PIL\n(Pillow)'), ('employee', 'sqlite3'),
        # product imports
        ('product', 'tkinter'), ('product', 'PIL\n(Pillow)'), ('product', 'sqlite3'),
        # supplier imports
        ('supplier', 'tkinter'), ('supplier', 'PIL\n(Pillow)'), ('supplier', 'sqlite3'),
        # sales imports
        ('sales', 'tkinter'), ('sales', 'PIL\n(Pillow)'), ('sales', 'sqlite3'),
        ('sales', 'os'),
        # DB / filesystem access
        ('dashboard', 'ims.db\n(SQLite)'), ('billing', 'ims.db\n(SQLite)'),
        ('category', 'ims.db\n(SQLite)'), ('employee', 'ims.db\n(SQLite)'),
        ('product', 'ims.db\n(SQLite)'), ('supplier', 'ims.db\n(SQLite)'),
        ('billing', 'bill/\n(filesystem)'), ('sales', 'bill/\n(filesystem)'),
    ]
    G.add_edges_from(edges)

    # Custom layout
    pos = {
        'dashboard':        (4.5, 8),
        'billing':          (8.5, 8),
        'category':         (0.5, 5.5),
        'employee':         (2.5, 5.5),
        'product':          (4.5, 5.5),
        'supplier':         (6.5, 5.5),
        'sales':            (8.5, 5.5),
        'tkinter':          (1.5, 2.5),
        'PIL\n(Pillow)':    (4.5, 2.5),
        'sqlite3':          (6.5, 2.5),
        'os':               (8.5, 2.5),
        'time':             (10.5, 2.5),
        'tempfile':         (12.5, 2.5),
        'ims.db\n(SQLite)': (2.5, 0.5),
        'bill/\n(filesystem)': (8.5, 0.5),
    }

    color_map = {
        'project':  '#4a90d9',
        'stdlib':   '#7dba5e',
        'third':    '#e8a838',
        'external': '#d0694a',
    }
    node_colors = [color_map[G.nodes[n]['kind']] for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2200,
                           alpha=0.92, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=7.5, font_weight='bold',
                            font_color='white', ax=ax)

    # Separate edge colors by target kind
    proj_edges  = [(u, v) for u, v in G.edges() if G.nodes[v]['kind'] == 'project']
    std_edges   = [(u, v) for u, v in G.edges() if G.nodes[v]['kind'] == 'stdlib']
    third_edges = [(u, v) for u, v in G.edges() if G.nodes[v]['kind'] == 'third']
    ext_edges   = [(u, v) for u, v in G.edges() if G.nodes[v]['kind'] == 'external']

    nx.draw_networkx_edges(G, pos, edgelist=proj_edges,  edge_color='#4a90d9',
                           arrows=True, arrowsize=15, width=1.5,
                           connectionstyle='arc3,rad=0.1', ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=std_edges,   edge_color='#7dba5e',
                           arrows=True, arrowsize=12, width=1.0, alpha=0.7,
                           connectionstyle='arc3,rad=0.0', ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=third_edges, edge_color='#e8a838',
                           arrows=True, arrowsize=12, width=1.0, alpha=0.7,
                           connectionstyle='arc3,rad=0.0', ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=ext_edges,   edge_color='#d0694a',
                           arrows=True, arrowsize=14, width=1.5,
                           connectionstyle='arc3,rad=0.15', ax=ax)

    # Legend
    legend_items = [
        mpatches.Patch(color='#4a90d9', label='Project module'),
        mpatches.Patch(color='#7dba5e', label='Python stdlib'),
        mpatches.Patch(color='#e8a838', label='Third-party (Pillow)'),
        mpatches.Patch(color='#d0694a', label='External resource (DB / Files)'),
    ]
    ax.legend(handles=legend_items, loc='lower left', fontsize=9, framealpha=0.9)

    ax.set_axis_off()
    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'diagram_dependency.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#f0f4f8')
    plt.close()
    print(f'Saved: {path}')


if __name__ == '__main__':
    draw_class_diagram()
    draw_sequence_diagram()
    draw_dependency_graph()
    print('All diagrams generated.')
