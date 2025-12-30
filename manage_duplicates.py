#!/usr/bin/env python3
"""
Script pour analyser et nettoyer les doublons dans la base de données.

Usage:
    python manage_duplicates.py detect [--version VERSION]
    python manage_duplicates.py clean [--version VERSION] [--strategy latest|first] [--dry-run]
"""

import argparse
import asyncio
import sys
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path
sys.path.insert(0, '.')

from app.db.session import get_db
from app.medicaments.models import Medicament


async def detect_duplicates(version: str = None):
    """Détecter les doublons dans la base."""
    print("🔍 Détection des doublons...")
    print("=" * 60)
    
    async for db in get_db():
        # Construire la requête
        query = select(
            Medicament.code,
            Medicament.version_nomenclature,
            func.count(Medicament.id).label('count')
        ).where(
            Medicament.deleted == False
        )
        
        if version:
            query = query.where(Medicament.version_nomenclature == version)
            print(f"📋 Version filtrée: {version}")
        else:
            print("📋 Toutes les versions")
        
        query = query.group_by(
            Medicament.code,
            Medicament.version_nomenclature
        ).having(
            func.count(Medicament.id) > 1
        )
        
        result = await db.execute(query)
        duplicates = result.all()
        
        print(f"\n✅ {len(duplicates)} groupes de doublons trouvés\n")
        
        if duplicates:
            total_extra = 0
            for dup in duplicates:
                print(f"  • Code: {dup.code:15s} | Version: {dup.version_nomenclature:15s} | Nombre: {dup.count}")
                total_extra += (dup.count - 1)
            
            print(f"\n📊 Total d'entrées en double: {total_extra}")
            print(f"💾 Espace libérable: ~{total_extra} enregistrements")
        else:
            print("✨ Aucun doublon détecté !")
        
        break


async def clean_duplicates(version: str = None, strategy: str = "latest", dry_run: bool = True):
    """Nettoyer les doublons."""
    action = "SIMULATION" if dry_run else "NETTOYAGE RÉEL"
    print(f"🧹 {action} des doublons...")
    print("=" * 60)
    
    if version:
        print(f"📋 Version: {version}")
    else:
        print("📋 Toutes les versions")
    
    print(f"📌 Stratégie: Garder l'{strategy} enregistrement")
    
    if dry_run:
        print("⚠️  MODE DRY-RUN - Aucune modification ne sera effectuée")
    else:
        print("⚠️  MODE ACTIF - Les doublons seront supprimés !")
        response = input("\nÊtes-vous sûr de vouloir continuer ? (oui/non): ")
        if response.lower() != "oui":
            print("❌ Opération annulée")
            return
    
    print()
    
    async for db in get_db():
        # Trouver les codes en double
        dup_query = select(
            Medicament.code,
            Medicament.version_nomenclature,
            func.count(Medicament.id).label('count')
        ).where(
            Medicament.deleted == False
        )
        
        if version:
            dup_query = dup_query.where(Medicament.version_nomenclature == version)
        
        dup_query = dup_query.group_by(
            Medicament.code,
            Medicament.version_nomenclature
        ).having(
            func.count(Medicament.id) > 1
        )
        
        dup_result = await db.execute(dup_query)
        duplicates = dup_result.all()
        
        if not duplicates:
            print("✨ Aucun doublon à nettoyer !")
            break
        
        total_deleted = 0
        
        # Traiter chaque groupe de doublons
        for idx, dup in enumerate(duplicates, 1):
            print(f"\n[{idx}/{len(duplicates)}] Traitement: {dup.code} (v{dup.version_nomenclature})")
            
            # Récupérer toutes les entrées pour ce code/version
            entries_query = select(Medicament).where(
                Medicament.code == dup.code,
                Medicament.version_nomenclature == dup.version_nomenclature,
                Medicament.deleted == False
            ).order_by(
                Medicament.created_at.desc() if strategy == "latest" else Medicament.created_at.asc()
            )
            
            entries_result = await db.execute(entries_query)
            entries = entries_result.scalars().all()
            
            if len(entries) > 1:
                # Garder la première entrée, supprimer les autres
                kept = entries[0]
                print(f"  ✅ Garde: ID={kept.id} | {kept.dci} - {kept.nom_marque} | Créé: {kept.created_at}")
                
                for entry in entries[1:]:
                    print(f"  ❌ Supprime: ID={entry.id} | {entry.dci} - {entry.nom_marque} | Créé: {entry.created_at}")
                    
                    if not dry_run:
                        entry.deleted = True
                    
                    total_deleted += 1
        
        if not dry_run:
            await db.commit()
            print(f"\n💾 Modifications enregistrées en base de données")
        
        print(f"\n{'=' * 60}")
        print(f"✅ Terminé !")
        print(f"📊 Groupes traités: {len(duplicates)}")
        print(f"🗑️  Entrées supprimées: {total_deleted}")
        
        if dry_run:
            print(f"\n💡 Pour appliquer les changements, exécutez:")
            print(f"   python manage_duplicates.py clean --strategy {strategy} --no-dry-run")
        
        break


def main():
    parser = argparse.ArgumentParser(
        description="Gestion des doublons dans la base de données NPP"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande detect
    detect_parser = subparsers.add_parser('detect', help='Détecter les doublons')
    detect_parser.add_argument(
        '--version',
        type=str,
        help='Filtrer par version de nomenclature'
    )
    
    # Commande clean
    clean_parser = subparsers.add_parser('clean', help='Nettoyer les doublons')
    clean_parser.add_argument(
        '--version',
        type=str,
        help='Filtrer par version de nomenclature'
    )
    clean_parser.add_argument(
        '--strategy',
        choices=['latest', 'first'],
        default='latest',
        help="Quelle entrée garder: 'latest' (plus récente) ou 'first' (plus ancienne)"
    )
    clean_parser.add_argument(
        '--no-dry-run',
        action='store_true',
        help='Appliquer les modifications (par défaut: simulation uniquement)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Exécuter la commande appropriée
    if args.command == 'detect':
        asyncio.run(detect_duplicates(version=args.version))
    elif args.command == 'clean':
        asyncio.run(clean_duplicates(
            version=args.version,
            strategy=args.strategy,
            dry_run=not args.no_dry_run
        ))


if __name__ == '__main__':
    main()
