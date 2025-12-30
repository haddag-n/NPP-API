#!/usr/bin/env python3
"""
Script pour afficher les noms des colonnes du fichier Excel.
"""

import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python check_excel_columns.py <fichier.xlsx>")
    sys.exit(1)

fichier = sys.argv[1]

try:
    # Lire le fichier Excel
    excel_file = pd.ExcelFile(fichier)
    
    print(f"📁 Fichier: {fichier}")
    print(f"📊 Nombre de feuilles: {len(excel_file.sheet_names)}")
    print()
    
    for sheet_name in excel_file.sheet_names:
        print(f"📋 Feuille: {sheet_name}")
        print("=" * 80)
        
        # Lire avec header=None pour voir les premières lignes
        df = pd.read_excel(fichier, sheet_name=sheet_name, header=None, nrows=30)
        
        print("\n🔍 Premières 30 lignes (brutes):")
        for idx, row in df.iterrows():
            row_str = [str(x)[:50] for x in row[:10] if pd.notna(x)]
            if row_str:  # Only show non-empty rows
                print(f"  Ligne {idx}: {row_str}")
        
        # Essayer de détecter l'en-tête automatiquement
        print("\n🔍 Tentative de détection de l'en-tête...")
        for idx, row in df.iterrows():
            row_values = [str(val).strip().upper() for val in row if pd.notna(val)]
            if any(keyword in ' '.join(row_values) for keyword in ['CODE', 'DCI', 'NOM']):
                print(f"  ✅ En-tête détecté à la ligne {idx}")
                
                # Lire avec cet en-tête
                df_with_header = pd.read_excel(fichier, sheet_name=sheet_name, header=idx)
                print(f"\n📌 Colonnes détectées ({len(df_with_header.columns)}):")
                for i, col in enumerate(df_with_header.columns):
                    print(f"  {i+1:2d}. '{col}'")
                
                # Afficher un échantillon de données
                print(f"\n📊 Échantillon de données (3 premières lignes):")
                print(df_with_header.head(3).to_string())
                break
        
        print("\n" + "=" * 80 + "\n")

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
