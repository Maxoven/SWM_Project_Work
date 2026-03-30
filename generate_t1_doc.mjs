import {
  Document, Packer, Paragraph, TextRun, ImageRun,
  HeadingLevel, AlignmentType, PageNumber, Header, Footer,
  BorderStyle, Table, TableRow, TableCell, WidthType, ShadingType,
  VerticalAlign
} from 'docx';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, size: 28, font: 'Arial' })],
    spacing: { before: 400, after: 200 },
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, size: 24, font: 'Arial' })],
    spacing: { before: 280, after: 160 },
  });
}

function para(text, { bold = false, italic = false, size = 22, spacing = 160 } = {}) {
  return new Paragraph({
    children: [new TextRun({ text, bold, italic, size, font: 'Arial' })],
    spacing: { after: spacing },
  });
}

function bullet(text) {
  return new Paragraph({
    bullet: { level: 0 },
    children: [new TextRun({ text, size: 22, font: 'Arial' })],
    spacing: { after: 80 },
  });
}

function imageBlock(imgPath, widthEmu, heightEmu, caption) {
  const data = fs.readFileSync(imgPath);
  const ext = path.extname(imgPath).slice(1).toLowerCase();
  const items = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new ImageRun({
          type: ext,
          data,
          transformation: { width: widthEmu, height: heightEmu },
          altText: { title: caption, description: caption, name: caption },
        }),
      ],
      spacing: { before: 200, after: 100 },
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: caption, italic: true, size: 18, font: 'Arial', color: '555555' })],
      spacing: { after: 300 },
    }),
  ];
  return items;
}

function tableRow(cells, isHeader = false) {
  const shade = isHeader
    ? { fill: '2C3E50', type: ShadingType.CLEAR }
    : { fill: 'FFFFFF', type: ShadingType.CLEAR };
  const fontColor = isHeader ? 'FFFFFF' : '000000';
  const border = { style: BorderStyle.SINGLE, size: 1, color: 'AAAAAA' };
  const borders = { top: border, bottom: border, left: border, right: border };

  return new TableRow({
    children: cells.map(text =>
      new TableCell({
        borders,
        shading: shade,
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        width: { size: Math.floor(9360 / cells.length), type: WidthType.DXA },
        children: [
          new Paragraph({
            children: [new TextRun({ text, bold: isHeader, size: 20, font: 'Arial', color: fontColor })],
          }),
        ],
      })
    ),
  });
}

const border = { style: BorderStyle.SINGLE, size: 1, color: 'AAAAAA' };
const borders = { top: border, bottom: border, left: border, right: border };

function infoTable(rows) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2500, 6860],
    rows: rows.map(([k, v], i) =>
      new TableRow({
        children: [
          new TableCell({
            borders,
            shading: { fill: 'EBF5FB', type: ShadingType.CLEAR },
            margins: { top: 60, bottom: 60, left: 120, right: 120 },
            width: { size: 2500, type: WidthType.DXA },
            children: [new Paragraph({ children: [new TextRun({ text: k, bold: true, size: 20, font: 'Arial' })] })],
          }),
          new TableCell({
            borders,
            shading: { fill: 'FFFFFF', type: ShadingType.CLEAR },
            margins: { top: 60, bottom: 60, left: 120, right: 120 },
            width: { size: 6860, type: WidthType.DXA },
            children: [new Paragraph({ children: [new TextRun({ text: v, size: 20, font: 'Arial' })] })],
          }),
        ],
      })
    ),
  });
}

// ── Build document ──────────────────────────────────────────────────────────

const children = [
  // ── Cover ─────────────────────────────────────────────────────────────
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 2000, after: 200 },
    children: [new TextRun({ text: 'CT70A3000 Software Maintenance', size: 36, bold: true, font: 'Arial', color: '010c48' })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: 'Spring 2026 — Project Report', size: 30, font: 'Arial', color: '333333' })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: 'T1: Code Comprehension', size: 32, bold: true, font: 'Arial', color: '2980B9' })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 2000 },
    children: [new TextRun({ text: 'Inventory Management System (IMS)', size: 26, italic: true, font: 'Arial', color: '555555' })],
  }),
  new Paragraph({ children: [new TextRun({ text: '', size: 22 })], pageBreakBefore: true }),

  // ── 1. Architecture overview ───────────────────────────────────────────
  heading1('1. System Architecture Overview'),
  para(
    'The Inventory Management System (IMS) is a desktop application built entirely in Python 3.12. '
    + 'It uses the standard-library Tkinter framework for its graphical user interface and SQLite as '
    + 'its embedded relational database. Bills (customer receipts) are persisted as plain-text files '
    + 'on the local filesystem.'
  ),
  para('The codebase consists of seven source modules plus a database initialisation script:', { bold: false }),

  infoTable([
    ['dashboard.py',  'Application entry-point. Creates the main Tk window, left-side navigation menu, and dashboard summary tiles. Instantiates all feature windows.'],
    ['billing.py',    'Full billing screen. Shows active products, manages a shopping cart, computes totals with a 5 % discount, and generates/prints customer receipts.'],
    ['product.py',    'CRUD screen for products. Reads category and supplier names from the DB for combo-box population.'],
    ['category.py',   'CRUD screen for product categories (add / delete).'],
    ['supplier.py',   'CRUD screen for suppliers (invoice-based, with contact and description).'],
    ['employee.py',   'CRUD screen for employees (personal details, role, salary).'],
    ['sales.py',      'Read-only view of previously generated bill files stored in bill/.'],
    ['create_db.py',  'One-time script that creates the ims.db SQLite database and its five tables.'],
  ]),

  new Paragraph({ spacing: { after: 200 } }),

  heading2('1.1 Architectural Pattern'),
  para(
    'The system follows a monolithic desktop-application architecture with a thin-layer separation between '
    + 'UI and data access. Each feature class contains its own Tkinter widget setup, event handlers, and '
    + 'direct SQLite calls — there is no explicit Model-View-Controller separation, but the classes '
    + 'map naturally to the View+Controller role while the SQLite tables serve as the Model.'
  ),

  heading2('1.2 Data Model'),
  para('The SQLite database ims.db contains the following tables:'),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1800, 7560],
    rows: [
      tableRow(['Table', 'Columns'], true),
      tableRow(['employee', 'eid (PK), name, email, gender, contact, dob, doj, pass, utype, address, salary']),
      tableRow(['supplier', 'invoice (PK), name, contact, desc']),
      tableRow(['category', 'cid (PK AUTOINCREMENT), name']),
      tableRow(['product', 'pid (PK AUTOINCREMENT), Category, Supplier, name, price, qty, status']),
      tableRow(['bill files', 'Not a DB table — stored as bill/{invoice_no}.txt on the filesystem']),
    ],
  }),

  new Paragraph({ spacing: { after: 200 } }),
  heading2('1.3 Technology Stack'),

  new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2200, 7160],
    rows: [
      tableRow(['Component', 'Technology'], true),
      tableRow(['Language', 'Python 3.12']),
      tableRow(['GUI Framework', 'Tkinter (stdlib) + ttk']),
      tableRow(['Database', 'SQLite 3 via sqlite3 stdlib module']),
      tableRow(['Image handling', 'Pillow (Pillow 12.1.0)']),
      tableRow(['Bill storage', 'Plain-text files (.txt) in bill/ directory']),
      tableRow(['Runtime', 'Single-process desktop app; no server or network layer']),
    ],
  }),

  new Paragraph({ children: [new TextRun({ text: '' })], pageBreakBefore: true }),

  // ── 2. Class Diagram ──────────────────────────────────────────────────
  heading1('2. Class Diagram'),
  para(
    'The diagram below shows all seven application classes, their key attributes and methods, '
    + 'and the relationships between them. Blue arrows denote instantiation (the IMS dashboard '
    + 'creates each feature window). Green arrows represent DB read dependencies, and red arrows '
    + 'represent DB read/write dependencies.'
  ),
  ...imageBlock(
    path.join(__dirname, 'diagram_class.png'),
    620, 380,
    'Figure 1 — Class Diagram'
  ),

  heading2('Key Relationships'),
  bullet('IMS (dashboard) creates instances of all five feature classes inside Toplevel windows.'),
  bullet('productClass reads category and supplier names from the DB to populate combo-boxes.'),
  bullet('billClass reads the product table (to list available stock) and writes back updated quantities and status after a sale.'),
  bullet('salesClass reads bill text files from the filesystem (bill/ directory) — it does not interact with the DB.'),
  bullet('All classes that perform CRUD open their own sqlite3 connection per method call (no shared connection object).'),

  new Paragraph({ children: [new TextRun({ text: '' })], pageBreakBefore: true }),

  // ── 3. Sequence Diagram ───────────────────────────────────────────────
  heading1('3. Sequence Diagram'),
  para(
    'The sequence diagram below illustrates the most complex workflow in the system: '
    + 'generating a customer bill. This flow involves four participants — the User, '
    + 'the billClass UI, the SQLite database, and the filesystem — and captures all '
    + 'state changes that occur when a sale is completed.'
  ),
  ...imageBlock(
    path.join(__dirname, 'diagram_sequence.png'),
    620, 440,
    'Figure 2 — Sequence Diagram: Generate Bill Workflow'
  ),

  heading2('Workflow Description'),
  para('The bill-generation workflow proceeds in the following steps:'),
  bullet('1. The user selects a product from the product table; billClass calls show() which queries the DB for Active products.'),
  bullet('2. The user selects a row — get_data() populates the product-detail fields.'),
  bullet('3. The user enters a quantity and clicks "Add | Update Cart" — add_update_cart() appends to cart_list.'),
  bullet('4. bill_update() recalculates the bill amount, 5 % discount, and net pay labels.'),
  bullet('5. The user enters customer name and contact, then clicks "Generate Bill".'),
  bullet('6. bill_top() writes the receipt header (invoice number, date, customer info) to the text area.'),
  bullet('7. bill_middle() iterates cart_list: for each item it updates the product qty and status in the DB.'),
  bullet('8. bill_bottom() appends totals. The full receipt text is saved to bill/{invoice}.txt.'),
  bullet('9. A success dialog is shown to the user.'),

  new Paragraph({ children: [new TextRun({ text: '' })], pageBreakBefore: true }),

  // ── 4. Dependency Graph ───────────────────────────────────────────────
  heading1('4. Module Dependency Graph'),
  para(
    'The graph below maps every import-level dependency in the project. '
    + 'Blue nodes are project modules, green nodes are Python standard-library modules, '
    + 'the orange node is the Pillow third-party library, and red nodes are external '
    + 'resources (the SQLite database file and the bill/ directory).'
  ),
  ...imageBlock(
    path.join(__dirname, 'diagram_dependency.png'),
    620, 400,
    'Figure 3 — Module Dependency Graph'
  ),

  heading2('Observations'),
  bullet('dashboard.py is the only module that imports other project modules — it acts as the composition root.'),
  bullet('billing.py is completely independent of the other five feature modules; it accesses the DB directly.'),
  bullet('All six feature modules share the same three external dependencies: tkinter, Pillow, and sqlite3.'),
  bullet('category.py contains a hardcoded absolute path ("Inventory-Management-System/images/...") which will fail when the project is run from a different working directory — a finding addressed in T2 (Refactoring).'),
  bullet('All modules open a new sqlite3 connection per method call rather than reusing a shared connection — a code-quality concern also addressed in T2.'),
];

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: 'Arial', size: 22 } },
    },
    paragraphStyles: [
      {
        id: 'Heading1', name: 'Heading 1',
        basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 28, bold: true, font: 'Arial', color: '010c48' },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2', name: 'Heading 2',
        basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: 'Arial', color: '2980B9' },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 },
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1080, bottom: 1440, left: 1080 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: '2C3E50', space: 1 } },
              children: [
                new TextRun({ text: 'CT70A3000 Software Maintenance  |  T1: Code Comprehension', size: 18, font: 'Arial', color: '555555' }),
              ],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              border: { top: { style: BorderStyle.SINGLE, size: 4, color: 'AAAAAA', space: 1 } },
              children: [
                new TextRun({ text: 'Page ', size: 18, font: 'Arial', color: '888888' }),
                new TextRun({ children: [PageNumber.CURRENT], size: 18, font: 'Arial', color: '888888' }),
              ],
            }),
          ],
        }),
      },
      children,
    },
  ],
});

const buf = await Packer.toBuffer(doc);
const outPath = path.join(__dirname, 'T1_Code_Comprehension.docx');
fs.writeFileSync(outPath, buf);
console.log('Written:', outPath);
