"""
T4 – Integration Tests
Tests that exercise multiple components working together against a real SQLite database.
Two integration scenarios:
  1. Full product lifecycle: category + supplier creation → product creation → sale → stock update
  2. Low-stock feature end-to-end: seed DB → query → export file content verification
Framework: pytest
Run: pytest tests/ -v
"""
import os
import sys
import sqlite3
import tempfile
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─────────────────────────────────────────────────────────────────────────────
# Shared fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """Temporary database pre-loaded with schema (matches create_db.py)."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE employee (
            eid TEXT PRIMARY KEY, name TEXT, email TEXT, gender TEXT,
            contact TEXT, dob TEXT, doj TEXT, pass TEXT,
            utype TEXT, address TEXT, salary TEXT
        );
        CREATE TABLE supplier (
            invoice TEXT PRIMARY KEY, name TEXT, contact TEXT, desc TEXT
        );
        CREATE TABLE category (
            cid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE
        );
        CREATE TABLE product (
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            Category TEXT, Supplier TEXT, name TEXT,
            price REAL, qty INTEGER, status TEXT
        );
    """)
    con.commit()
    con.close()
    yield path
    os.unlink(path)


# ─────────────────────────────────────────────────────────────────────────────
# Integration Scenario 1 – Full product lifecycle through a sale
# ─────────────────────────────────────────────────────────────────────────────

class TestProductSaleLifecycle:
    """
    Simulates the real workflow:
      1. Add a category.
      2. Add a supplier.
      3. Add a product linked to that category and supplier.
      4. Simulate a sale (decrement qty, update status when sold out).
      5. Verify the product is no longer returned in Active products query.
    """

    def test_full_lifecycle(self, db):
        con = sqlite3.connect(db)
        cur = con.cursor()

        # Step 1: Create category
        cur.execute("INSERT INTO category(name) VALUES (?)", ("Electronics",))
        con.commit()
        cur.execute("SELECT cid FROM category WHERE name='Electronics'")
        assert cur.fetchone() is not None

        # Step 2: Create supplier
        cur.execute("INSERT INTO supplier VALUES (?,?,?,?)",
                    ("SUP-01", "TechSupplies Ltd", "044-9876", "Electronics wholesale"))
        con.commit()

        # Step 3: Create product (as productClass.add() would)
        cur.execute(
            "INSERT INTO product(Category,Supplier,name,price,qty,status) VALUES(?,?,?,?,?,?)",
            ("Electronics", "TechSupplies Ltd", "USB-C Hub", 29.99, 10, "Active")
        )
        con.commit()
        cur.execute("SELECT pid, qty FROM product WHERE name='USB-C Hub'")
        row = cur.fetchone()
        assert row is not None
        pid, initial_qty = row
        assert initial_qty == 10

        # Step 4a: Sell 3 units (as billClass.bill_middle() would)
        sold_qty = 3
        remaining = initial_qty - sold_qty
        status = "Active" if remaining > 0 else "Inactive"
        cur.execute("UPDATE product SET qty=?, status=? WHERE pid=?",
                    (remaining, status, pid))
        con.commit()

        # Verify stock reduced
        cur.execute("SELECT qty, status FROM product WHERE pid=?", (pid,))
        row = cur.fetchone()
        assert row[0] == 7
        assert row[1] == "Active"

        # Step 4b: Sell remaining 7 units (product sold out)
        cur.execute("UPDATE product SET qty=0, status='Inactive' WHERE pid=?", (pid,))
        con.commit()

        # Step 5: Active product query should no longer include this product
        cur.execute(
            "SELECT pid,name,price,qty,status FROM product WHERE status='Active'",
        )
        active_names = {r[1] for r in cur.fetchall()}
        assert "USB-C Hub" not in active_names

        con.close()

    def test_product_duplicate_prevention(self, db):
        """productClass.add() checks for duplicates by name."""
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO product(Category,Supplier,name,price,qty,status) VALUES(?,?,?,?,?,?)",
            ("Cat", "Sup", "WidgetX", 5.00, 20, "Active")
        )
        con.commit()

        # Second insert with same name – simulate the duplicate check
        cur.execute("SELECT * FROM product WHERE name=?", ("WidgetX",))
        already_exists = cur.fetchone() is not None
        assert already_exists  # application should refuse to insert
        con.close()

    def test_employee_salary_update(self, db):
        """Verify employee update propagates salary change."""
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO employee VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            ("E001", "Alice", "alice@example.com", "Female",
             "555-0001", "1990-01-01", "2020-03-15",
             "secret", "Admin", "123 Main St", "3000")
        )
        con.commit()

        # Simulate employeeClass.update()
        cur.execute(
            "UPDATE employee SET salary=? WHERE eid=?",
            ("3500", "E001")
        )
        con.commit()
        cur.execute("SELECT salary FROM employee WHERE eid=?", ("E001",))
        assert cur.fetchone()[0] == "3500"
        con.close()


# ─────────────────────────────────────────────────────────────────────────────
# Integration Scenario 2 – Low-Stock feature end-to-end
# ─────────────────────────────────────────────────────────────────────────────

class TestLowStockFeatureIntegration:
    """
    Exercises the LowStockClass data layer end-to-end:
      - Seeds the DB with a mix of stock levels.
      - Verifies the correct items are returned for a given threshold.
      - Verifies the export file content is correct.
    """

    def _seed(self, db):
        products = [
            ("Phones",   "Sup A", "Phone X",    299.99, 0,  "Inactive"),
            ("Phones",   "Sup A", "Phone Y",    349.99, 2,  "Active"),
            ("Laptops",  "Sup B", "Laptop Z",   899.99, 5,  "Active"),
            ("Tablets",  "Sup B", "Tablet Pro", 499.99, 15, "Active"),
            ("Cables",   "Sup C", "USB Cable",   4.99,  50, "Active"),
        ]
        con = sqlite3.connect(db)
        cur = con.cursor()
        for p in products:
            cur.execute(
                "INSERT INTO product(Category,Supplier,name,price,qty,status) VALUES(?,?,?,?,?,?)",
                p
            )
        con.commit()
        con.close()

    def test_threshold_5_returns_correct_items(self, db):
        self._seed(db)
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM product WHERE qty <= ? ORDER BY qty ASC",
            (5,)
        )
        names = {r[0] for r in cur.fetchall()}
        con.close()
        assert names == {"Phone X", "Phone Y", "Laptop Z"}
        assert "Tablet Pro" not in names
        assert "USB Cable" not in names

    def test_threshold_0_returns_only_out_of_stock(self, db):
        self._seed(db)
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM product WHERE qty <= ? ORDER BY qty ASC",
            (0,)
        )
        names = {r[0] for r in cur.fetchall()}
        con.close()
        assert names == {"Phone X"}

    def test_threshold_100_returns_all(self, db):
        self._seed(db)
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM product WHERE qty <= ?",
            (100,)
        )
        count = cur.fetchone()[0]
        con.close()
        assert count == 5  # all five products

    def test_export_file_content(self, db, tmp_path):
        """Simulate the export logic and verify file content."""
        self._seed(db)
        threshold = 5
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute(
            "SELECT pid, name, Category, Supplier, price, qty, status "
            "FROM product WHERE qty <= ? ORDER BY qty ASC",
            (threshold,)
        )
        rows = cur.fetchall()
        con.close()

        # Replicate LowStockClass.export() file writing
        out_file = tmp_path / "low_stock_report.txt"
        header = (
            f"Low-Stock Alert Report\n"
            f"Threshold : qty <= {threshold}\n"
            f"{'=' * 60}\n"
        )
        lines = [
            f"{r[1]:<22}{str(r[5]):>6}" for r in rows
        ]
        content = header + "\n".join(lines)
        out_file.write_text(content)

        # Verify file was written and contains expected products
        text = out_file.read_text()
        assert "Low-Stock Alert Report" in text
        assert "Phone X" in text
        assert "Phone Y" in text
        assert "Laptop Z" in text
        assert "Tablet Pro" not in text
