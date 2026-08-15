import os
import pandas as pd
from src.database.connection import get_connection

def main():
    conn = get_connection()
    
    with open("C:/Users/techn/.gemini/antigravity/brain/c578f0ac-bf47-4620-907f-169c64a23cf3/analytics_baseline.md", "w") as f:
        f.write("# Core Data Quality & Analytics Baseline\n\n")

        # 1. Worker Coverage
        f.write("## 1. Worker Coverage\n")
        
        counts = pd.read_sql("SELECT COUNT(*) as c FROM core.workers", conn)
        f.write(f"- **Total workers**: {counts.iloc[0]['c']}\n")
        
        per_source = pd.read_sql("""
            SELECT source_name, COUNT(DISTINCT worker_id) as workers 
            FROM core.worker_source_records 
            GROUP BY source_name
        """, conn)
        f.write("- **Workers per source**:\n")
        for _, row in per_source.iterrows():
            f.write(f"  - {row['source_name']}: {row['workers']}\n")
            
        overlap = pd.read_sql("""
            SELECT sources_count, COUNT(*) as workers
            FROM (
                SELECT worker_id, COUNT(DISTINCT source_name) as sources_count
                FROM core.worker_source_records
                GROUP BY worker_id
            ) t
            GROUP BY sources_count
            ORDER BY sources_count
        """, conn)
        f.write("- **Workers appearing in X sources**:\n")
        for _, row in overlap.iterrows():
            f.write(f"  - {row['sources_count']} sources: {row['workers']}\n")

        # 2. Skills
        f.write("\n## 2. Skills\n")
        skill_count = pd.read_sql("SELECT COUNT(*) as c FROM core.skills", conn)
        f.write(f"- **Total canonical skills**: {skill_count.iloc[0]['c']}\n")
        
        top_skills = pd.read_sql("""
            SELECT s.skill_name, COUNT(DISTINCT ws.worker_id) as workers
            FROM core.skills s
            JOIN core.worker_skills ws ON s.skill_id = ws.skill_id
            GROUP BY s.skill_name
            ORDER BY workers DESC
            LIMIT 5
        """, conn)
        f.write("- **Most common skills**:\n")
        for _, row in top_skills.iterrows():
            f.write(f"  - {row['skill_name']} ({row['workers']} workers)\n")
            
        no_skills = pd.read_sql("""
            SELECT COUNT(*) as c FROM core.workers w
            WHERE NOT EXISTS (SELECT 1 FROM core.worker_skills ws WHERE ws.worker_id = w.worker_id)
        """, conn)
        f.write(f"- **Workers with no skills**: {no_skills.iloc[0]['c']}\n")
        
        source_skills = pd.read_sql("""
            SELECT source_name, COUNT(DISTINCT worker_id) as workers_with_skills, COUNT(*) as relation_records
            FROM core.worker_skills
            GROUP BY source_name
        """, conn)
        f.write("- **Source-wise skill distribution**:\n")
        for _, row in source_skills.iterrows():
            f.write(f"  - {row['source_name']}: {row['workers_with_skills']} workers, {row['relation_records']} tags\n")

        # 3. Naukri
        f.write("\n## 3. Naukri Analytics\n")
        naukri_exp = pd.read_sql("SELECT MIN(experience_years) as mn, AVG(experience_years) as av, MAX(experience_years) as mx FROM core.naukri_worker_data", conn)
        if not naukri_exp.empty:
            f.write(f"- **Experience distribution (years)**: Min: {naukri_exp.iloc[0]['mn']}, Avg: {float(naukri_exp.iloc[0]['av'] or 0):.2f}, Max: {naukri_exp.iloc[0]['mx']}\n")
        
        naukri_ctc = pd.read_sql("SELECT MIN(current_ctc) as mn, AVG(current_ctc) as av, MAX(current_ctc) as mx FROM core.naukri_worker_data", conn)
        if not naukri_ctc.empty:
            f.write(f"- **CTC distribution (INR)**: Min: {naukri_ctc.iloc[0]['mn']}, Avg: {float(naukri_ctc.iloc[0]['av'] or 0):.2f}, Max: {naukri_ctc.iloc[0]['mx']}\n")
        
        ctc_outliers = pd.read_sql("SELECT COUNT(*) as c FROM core.naukri_worker_data WHERE current_ctc < 100000 OR current_ctc > 5000000", conn)
        f.write(f"- **CTC Outliers (< 1L or > 50L)**: {ctc_outliers.iloc[0]['c']}\n")
        
        app_date = pd.read_sql("SELECT COUNT(*) as c, COUNT(applied_date) as c2 FROM core.naukri_worker_data", conn)
        f.write(f"- **Applied date coverage**: {app_date.iloc[0]['c2']} out of {app_date.iloc[0]['c']}\n")

        # 4. Gig
        f.write("\n## 4. Gig Analytics\n")
        gig_unit = pd.read_sql("SELECT rate_unit, COUNT(*) as c FROM core.gig_worker_data GROUP BY rate_unit", conn)
        f.write("- **Hourly vs Monthly workers**:\n")
        for _, row in gig_unit.iterrows():
            f.write(f"  - {row['rate_unit']}: {row['c']}\n")
            
        gig_rate = pd.read_sql("SELECT rate_unit, MIN(rate_amount) as mn, AVG(rate_amount) as av, MAX(rate_amount) as mx FROM core.gig_worker_data GROUP BY rate_unit", conn)
        f.write("- **Rate distribution**:\n")
        for _, row in gig_rate.iterrows():
            f.write(f"  - {row['rate_unit']}: Min: {row['mn']}, Avg: {float(row['av'] or 0):.2f}, Max: {row['mx']}\n")
            
        gig_status = pd.read_sql("SELECT status, COUNT(*) as c FROM core.gig_worker_data GROUP BY status", conn)
        f.write("- **Status distribution**:\n")
        for _, row in gig_status.iterrows():
            f.write(f"  - {row['status']}: {row['c']}\n")

        # 5. CBNexus
        f.write("\n## 5. CBNexus Analytics\n")
        cb_ver = pd.read_sql("SELECT verified, COUNT(*) as c FROM core.cbnexus_worker_data GROUP BY verified", conn)
        f.write("- **Verified vs Unverified**:\n")
        for _, row in cb_ver.iterrows():
            f.write(f"  - {row['verified']}: {row['c']}\n")
            
        cb_proj = pd.read_sql("SELECT MIN(projects_completed) as mn, AVG(projects_completed) as av, MAX(projects_completed) as mx FROM core.cbnexus_worker_data", conn)
        if not cb_proj.empty:
            f.write(f"- **Projects completed**: Min: {cb_proj.iloc[0]['mn']}, Avg: {float(cb_proj.iloc[0]['av'] or 0):.2f}, Max: {cb_proj.iloc[0]['mx']}\n")
        
        # 6. Cross-source enrichment
        f.write("\n## 6. Cross-source Enrichment\n")
        naukri_gig = pd.read_sql("""
            SELECT COUNT(*) as c FROM core.workers w
            WHERE EXISTS (SELECT 1 FROM core.naukri_worker_data n WHERE n.worker_id = w.worker_id)
              AND EXISTS (SELECT 1 FROM core.gig_worker_data g WHERE g.worker_id = w.worker_id)
        """, conn)
        f.write(f"- **Workers with Naukri + Gig**: {naukri_gig.iloc[0]['c']}\n")
        
        naukri_cb = pd.read_sql("""
            SELECT COUNT(*) as c FROM core.workers w
            WHERE EXISTS (SELECT 1 FROM core.naukri_worker_data n WHERE n.worker_id = w.worker_id)
              AND EXISTS (SELECT 1 FROM core.cbnexus_worker_data cb WHERE cb.worker_id = w.worker_id)
        """, conn)
        f.write(f"- **Workers with Naukri + CBNexus**: {naukri_cb.iloc[0]['c']}\n")
        
        all_three = pd.read_sql("""
            SELECT COUNT(*) as c FROM core.workers w
            WHERE EXISTS (SELECT 1 FROM core.naukri_worker_data n WHERE n.worker_id = w.worker_id)
              AND EXISTS (SELECT 1 FROM core.gig_worker_data g WHERE g.worker_id = w.worker_id)
              AND EXISTS (SELECT 1 FROM core.cbnexus_worker_data cb WHERE cb.worker_id = w.worker_id)
        """, conn)
        f.write(f"- **Workers present in all three sources**: {all_three.iloc[0]['c']}\n")

        # 7. Data-quality checks
        f.write("\n## 7. Data-quality Checks\n")
        missing_email = pd.read_sql("SELECT COUNT(*) as c FROM core.workers WHERE email IS NULL OR email = ''", conn)
        missing_phone = pd.read_sql("SELECT COUNT(*) as c FROM core.workers WHERE phone_10 IS NULL OR phone_10 = ''", conn)
        f.write(f"- **Missing email**: {missing_email.iloc[0]['c']}\n- **Missing phone**: {missing_phone.iloc[0]['c']}\n")
        
        dup_names = pd.read_sql("""
            SELECT canonical_name, COUNT(*) as c 
            FROM core.workers 
            GROUP BY canonical_name 
            HAVING COUNT(*) > 1
        """, conn)
        f.write(f"- **Duplicate canonical identities (same name)**: {dup_names.shape[0]}\n")
        
        orphan = pd.read_sql("""
            SELECT COUNT(*) as c FROM core.workers w
            WHERE NOT EXISTS (SELECT 1 FROM core.worker_source_records ws WHERE ws.worker_id = w.worker_id)
        """, conn)
        f.write(f"- **Orphan identities (no source records)**: {orphan.iloc[0]['c']}\n")

        invalid_phone = pd.read_sql("SELECT COUNT(*) as c FROM core.workers WHERE phone_10 IS NOT NULL AND phone_10 !~ '^[0-9]{10}$'", conn)
        f.write(f"- **Invalid normalized phone**: {invalid_phone.iloc[0]['c']}\n")
        
        dup_worker_skills = pd.read_sql("""
            SELECT worker_id, skill_id, COUNT(*) as c 
            FROM core.worker_skills 
            GROUP BY worker_id, skill_id 
            HAVING COUNT(*) > 1
        """, conn)
        f.write(f"- **Duplicate worker-skill relationships**: {dup_worker_skills.shape[0]}\n")
        
    conn.close()

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)
    main()
