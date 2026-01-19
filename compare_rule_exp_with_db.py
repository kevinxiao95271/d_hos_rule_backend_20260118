
import pymysql
import sys

# 数据库连接配置
DB_CONFIG = {
    'host': 'gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    'port': 63606,
    'user': 'root',
    'password': 'Yiguo9527_',
    'database': 'd_hosq_traegj_20260115',
    'charset': 'utf8mb4'
}

def compare_rules():
    print("Connecting to database...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Fetch all rules from DB
        print("Fetching rules from kiro_qc_rule...")
        cursor.execute("SELECT field_code, rule_type, description, deduct_score FROM kiro_qc_rule")
        db_rules = cursor.fetchall()
        
        db_rule_signatures = set()
        signature_to_rows = {}
        for r in db_rules:
            sig = (
                str(r['field_code']).strip() if r['field_code'] else '',
                str(r['rule_type']).strip() if r['rule_type'] else '',
                str(r['description']).strip() if r['description'] else ''
            )
            db_rule_signatures.add(sig)
            signature_to_rows.setdefault(sig, []).append(r)
            
        print(f"Fetched {len(db_rules)} rules from database.")
        
        # Read file
        file_path = 'D:\\rule_exp.txt'
        print(f"Reading file {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print(f"File has {len(lines)} lines.")

        processed_lines = 0
        matched_line_count = 0
        file_rule_signatures = set()

        missing_rules = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split('\t')
            if len(parts) < 6:
                # print(f"Skipping malformed line {i+1}: {line}")
                continue

            processed_lines += 1
            
            # File columns: field_name(0), field_code(1), level(2), deduct_score(3), rule_type(4), description(5)
            field_code = parts[1].strip()
            rule_type = parts[4].strip()
            description = parts[5].strip()
            
            sig = (field_code, rule_type, description)
            file_rule_signatures.add(sig)
            
            if sig not in db_rule_signatures:
                missing_rules.append({
                    'line': i + 1,
                    'content': line,
                    'field_code': field_code,
                    'rule_type': rule_type,
                    'description': description
                })
            else:
                matched_line_count += 1
        
        distinct_file_rules = len(file_rule_signatures)
        distinct_db_rules = len(db_rule_signatures)
        distinct_in_both = len(file_rule_signatures & db_rule_signatures)
        distinct_only_in_file = len(file_rule_signatures - db_rule_signatures)
        db_only_signatures = db_rule_signatures - file_rule_signatures
        distinct_only_in_db = len(db_only_signatures)

        print(f"\nProcessed {processed_lines} valid rule lines.")
        print(f"Distinct rules in file: {distinct_file_rules}")
        print(f"Distinct rules in database: {distinct_db_rules}")
        print(f"Distinct rules present in both: {distinct_in_both}")
        print(f"Distinct rules only in file (not in db): {distinct_only_in_file}")
        print(f"Distinct rules only in db (not in file): {distinct_only_in_db}")
        print(f"Line-level matches (file lines that have a matching rule in db): {matched_line_count}")

        if db_only_signatures:
            extra_output_file = "extra_rules_in_db.txt"
            with open(extra_output_file, "w", encoding="utf-8") as f:
                f.write("field_code\trule_type\tdeduct_score\tdescription\n")
                f.write("-" * 80 + "\n")
                for sig in db_only_signatures:
                    rows = signature_to_rows.get(sig, [])
                    for r in rows:
                        field_code = str(r['field_code']).strip() if r['field_code'] else ''
                        rule_type = str(r['rule_type']).strip() if r['rule_type'] else ''
                        deduct_score = str(r['deduct_score']) if r['deduct_score'] is not None else ''
                        description = str(r['description']).strip() if r['description'] else ''
                        f.write(f"{field_code}\t{rule_type}\t{deduct_score}\t{description}\n")

            print(f"\nExtra rules only in database have been saved to {extra_output_file}")
        print(f"\nFound {len(missing_rules)} missing rules.")
        
        
        if missing_rules:
            output_file = "missing_rules.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("Line\tField Code\tRule Type\tDescription\n")
                f.write("-" * 80 + "\n")
                for rule in missing_rules:
                    f.write(f"{rule['line']}\t{rule['field_code']}\t{rule['rule_type']}\t{rule['description']}\n")
            
            print(f"\nMissing rules have been saved to {output_file}")
            print("\nFirst 20 missing rules:")
            print("Line\tField Code\tRule Type\tDescription")
            print("-" * 80)
            for rule in missing_rules[:20]:
                print(f"{rule['line']}\t{rule['field_code']}\t{rule['rule_type']}\t{rule['description']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()


def clean_wrong_rc013_rules(dry_run=True):
    print("Connecting to database for RC013 cleanup...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        query = """
            SELECT id, field_name, field_code, rule_type, deduct_score, description
            FROM kiro_qc_rule
            WHERE description LIKE '%RC013字典范围%'
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        candidates = []
        for r in rows:
            field_name = (r["field_name"] or "").strip()
            description = (r["description"] or "").strip()
            if "麻醉方式" not in field_name and "麻醉方式" not in description:
                candidates.append(r)

        print(f"Total RC013-related rules: {len(rows)}")
        print(f"Non-anesthesia RC013 rules to be deleted: {len(candidates)}")

        backup_file = "deleted_rc013_non_anesthesia_rules.txt"
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write("id\tfield_name\tfield_code\trule_type\tdeduct_score\tdescription\n")
            f.write("-" * 80 + "\n")
            for r in candidates:
                f.write(
                    f"{r['id']}\t{r['field_name']}\t{r['field_code']}\t"
                    f"{r['rule_type']}\t{r['deduct_score']}\t{r['description']}\n"
                )

        print(f"Backup of candidates written to {backup_file}")

        if not dry_run and candidates:
            ids = [str(r["id"]) for r in candidates]
            id_list = ",".join(ids)
            delete_sql = f"DELETE FROM kiro_qc_rule WHERE id IN ({id_list})"
            print(f"Executing delete: {delete_sql}")
            cursor.execute(delete_sql)
            conn.commit()
            print(f"Deleted {cursor.rowcount} rows from kiro_qc_rule.")
        else:
            print("Dry run mode, no deletion executed.")
    except Exception as e:
        print(f"Error during RC013 cleanup: {e}")
    finally:
        if "conn" in locals() and conn.open:
            conn.close()

if __name__ == "__main__":
    compare_rules()
